"""Command-line entrypoint: `python -m blog_agent` or `blog-agent`."""

from __future__ import annotations
import argparse, sys
from blog_agent.pipeline import generate_blog

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="blog-agent", description="Generate a blog post.")
    parser.add_argument("topic")
    parser.add_argument("--as-of", dest="as_of", default=None)
    args = parser.parse_args(argv)

    state = generate_blog(topic=args.topic, as_of=args.as_of)
    print(f"\nBlog written to: {state.get('output_path')}\n")
    return 0

if __name__ == "__main__":
    raise sys.exit(main())