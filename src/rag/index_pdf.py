import asyncio

from src.config import load_config
from src.rag.indexer import ingest_company_pdfs


async def _main() -> None:
    config = load_config()
    indexed = await ingest_company_pdfs(config=config)
    print(f"Indexed chunks: {indexed}")


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
