"""Command-line entrypoint: `python -m blog_agent` or `blog-agent`."""

from __future__ import annotations
import argparse, sys
from dotenv import load_dotenv
load_dotenv()  # populate os.environ before LangChain imports read LANGCHAIN_* vars

from blog_agent.pipeline import generate_blog
from blog_agent.core import get_settings, configure_logging, get_logger

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="blog-agent", description="Generate a blog post.")
    parser.add_argument("topic")
    parser.add_argument("--as-of", dest="as_of", default=None)
    args = parser.parse_args(argv)

    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)
    logger = get_logger("cli")

    state = generate_blog(topic=args.topic, as_of=args.as_of)
    logger.info("cli.done", output_path=state.get("output_path"))
    print(f"\nBlog written to: {state.get('output_path')}\n")
    return 0

if __name__ == "__main__":
    raise sys.exit(main())