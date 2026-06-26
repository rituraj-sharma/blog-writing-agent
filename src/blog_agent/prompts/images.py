from langchain_core.prompts import ChatPromptTemplate

DECIDE_IMAGES_SYSTEM = """You are an expert technical editor.
Decide if images/diagrams are needed for THIS blog.

Rules:
- Max {max_images} images total.
- Each image must materially improve understanding (diagram/flow/table-like visual).
- Insert placeholders exactly: [[IMAGE_1]], [[IMAGE_2]], [[IMAGE_3]].
- If no images are needed: md_with_placeholders must equal the input and images=[].
- Prefer technical diagrams with short labels; avoid decorative images.
Return strictly a GlobalImagePlan.
"""

DECIDE_IMAGES_PROMPT = ChatPromptTemplate.from_messages([
    ("system", DECIDE_IMAGES_SYSTEM),
    ("human",
     "Blog kind: {blog_kind}\nTopic: {topic}\n\n"
     "Insert placeholders and propose image prompts.\n\n{merged_md}"),
])