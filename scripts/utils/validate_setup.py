"""
Validate Workshop Setup
=======================
Pre-workshop environment checker to ensure everything is ready.

Usage:
    python scripts/utils/validate_setup.py

Checks:
- Python version
- Required packages
- Environment variables
- Data files
- Vector database
- OpenAI API connection
"""

import sys
import os
from pathlib import Path
import importlib.util

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "restaurant"
CHROMA_DIR = BASE_DIR / "data" / "embeddings"
ENV_FILE = BASE_DIR / ".env"


def check_python_version():
    """Check Python version is 3.9+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} detected (need 3.9+)")
        return False


def check_package(package_name: str, import_name: str = None) -> bool:
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name

    spec = importlib.util.find_spec(import_name)
    if spec is not None:
        print(f"✓ {package_name} installed")
        return True
    else:
        print(f"✗ {package_name} NOT installed")
        return False


def check_env_file():
    """Check if .env file exists and has required variables"""
    if not ENV_FILE.exists():
        print(f"✗ .env file not found at {ENV_FILE}")
        print(f"  Copy .env.example to .env and add your API key")
        return False

    print(f"✓ .env file found")

    # Load and check for API key
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_FILE)

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            print(f"✓ OPENAI_API_KEY configured")
            return True
        else:
            print(f"✗ OPENAI_API_KEY not set or still has placeholder value")
            return False
    except ImportError:
        print(f"⚠ python-dotenv not installed, can't validate .env contents")
        return False


def check_openai_connection():
    """Test OpenAI API connection"""
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_FILE)

        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Make a minimal API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )

        if response.choices:
            print("✓ OpenAI API connection successful")
            return True
        else:
            print("✗ OpenAI API connection failed - unexpected response")
            return False

    except ImportError:
        print("⚠ Can't test OpenAI (openai package not installed)")
        return False
    except Exception as e:
        print(f"✗ OpenAI API connection failed: {str(e)[:100]}")
        return False


def check_data_files():
    """Check if all required data files exist"""
    required_files = [
        "menu.json",
        "business_info.json",
        "faq.md",
        "catering.md",
        "wine_list.md"
    ]

    all_exist = True
    print("✓ Sample data files:")

    for filename in required_files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"  ✓ {filename} ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ {filename} MISSING")
            all_exist = False

    return all_exist


def check_vector_db():
    """Check if vector database is initialized"""
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer

        if not CHROMA_DIR.exists():
            print("✗ Vector database not initialized")
            print("  Run: python scripts/utils/setup_vectordb.py")
            return False

        # Try to load collection
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_collection(name="restaurant_docs")

        count = collection.count()
        if count > 0:
            print(f"✓ Vector database initialized ({count} documents)")
            return True
        else:
            print("✗ Vector database empty")
            return False

    except ImportError:
        print("⚠ ChromaDB not installed - RAG features will be unavailable")
        print("  Install with: pip install chromadb sentence-transformers")
        return False
    except Exception as e:
        print(f"✗ Vector database not found: {e}")
        print("  Run: python scripts/utils/setup_vectordb.py")
        return False


def main():
    """Run all validation checks"""
    print("=" * 60)
    print("Workshop Setup Validation")
    print("=" * 60)

    results = []

    # Python version
    print("\n[1] Python Version")
    results.append(("Python 3.9+", check_python_version()))

    # Required packages
    print("\n[2] Required Packages")
    packages = [
        ("chainlit", "chainlit"),
        ("openai", "openai"),
        ("python-dotenv", "dotenv"),
        ("chromadb", "chromadb"),
        ("langchain", "langchain"),
        ("langchain-openai", "langchain_openai"),
        ("sentence-transformers", "sentence_transformers"),
        ("pydantic", "pydantic")
    ]

    all_packages_installed = True
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_packages_installed = False

    results.append(("All packages", all_packages_installed))

    # Environment file
    print("\n[3] Environment Configuration")
    results.append((".env file", check_env_file()))

    # OpenAI connection
    print("\n[4] OpenAI API Connection")
    results.append(("OpenAI API", check_openai_connection()))

    # Data files
    print("\n[5] Sample Data Files")
    results.append(("Data files", check_data_files()))

    # Vector database
    print("\n[6] Vector Database")
    results.append(("Vector DB", check_vector_db()))

    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} | {check_name}")

    print("\n" + "=" * 60)

    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        print("   Ready for workshop! 🎉")
        print("\n   To start a script, run:")
        print("   chainlit run scripts/01_bare_minimum_chatbot.py")
        return 0
    else:
        print(f"⚠️  {total - passed} check(s) failed ({passed}/{total} passed)")
        print("\n   Fix the issues above and run this script again.")

        if not results[1][1]:  # Packages not installed
            print("\n   To install all dependencies:")
            print("   pip install -e .")
            print("   or with uv:")
            print("   uv sync")

        return 1


if __name__ == "__main__":
    exit(main())
