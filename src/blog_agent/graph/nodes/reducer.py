"""Reducer subgraph nodes: merge sections → decide images → generate & persist."""

from __future__ import annotations
from pathlib import Path
from blog_agent.core import get_settings
from blog_agent.llm import get_llm
from blog_agent.prompts import DECIDE_IMAGES_PROMPT
from blog_agent.schemas import BlogState, GlobalImagePlan
from blog_agent.services import get_storage, get_image_service


def merge_content_node(state: BlogState) -> dict:
    plan = state['plan']
    assert plan is not None

    ordered = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered).strip()
    return {"merged_md": f"# {plan.blog_title}\n\n{body}\n"}


def decide_images_node(state: BlogState) -> dict:
    settings = get_settings()
    svc = get_image_service()
    if not svc.enabled:
        return {"md_with_placeholders": state.get("merged_md", ""), "image_specs": []}
    
    plan = state["plan"]
    chain = DECIDE_IMAGES_PROMPT | get_llm().with_structured_output(GlobalImagePlan)
    image_plan: GlobalImagePlan = chain.invoke({
        "max_images": settings.max_images,
        "blog_kind": plan.blog_kind,
        "topic": state["topic"],
        "merged_md": state["merged_md"]
    })

    specs = [img.model_dump() for img in image_plan.images][: settings.max_images]
    return {"md_with_placeholders": image_plan.md_with_placeholders, "image_specs": specs}


def generate_and_place_images_node(state: BlogState) -> dict:
    plan = state["plan"]
    storage = get_storage()
    image_service = get_image_service()

    md = state.get("md_with_placeholders") or state["merged_md"]
    specs = state.get("image_specs", []) or []

    for spec in specs:
        placeholder, filename = spec["placeholder"], spec["filename"]
        if not storage.image_exists(filename):
            try:
                data = image_service.generate(spec["prompt"])
                storage.write_image(filename, data)
            except Exception as exc:  # per-image graceful fallback
                md = md.replace(
                    placeholder,
                    f"> **[IMAGE GENERATION FAILED]** {spec.get('caption', '')}\n>\n"
                    f"> **Prompt:** {spec.get('prompt', '')}\n>\n"
                    f"> **Error:** {exc}\n",
                )
                continue
        md = md.replace(placeholder, f"![{spec['alt']}](images/{filename})\n*{spec['caption']}*")

    output_path = storage.write_markdown(plan.blog_title, md)
    return {"final": md, "output_path": str(output_path)}



