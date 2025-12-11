"""
Download Deutsche Bahn Daten von HuggingFace
"""

from huggingface_hub import hf_hub_download
import os

print("📥 Lade Deutsche Bahn Daten von HuggingFace...")
print("=" * 60)

try:
    file = hf_hub_download(
        repo_id='piebro/deutsche-bahn-data',
        filename='monthly_processed_data/data-2024-10.parquet',
        repo_type='dataset',
        local_dir='../Data/deutsche_bahn_data'
    )

    print("✅ Download erfolgreich!")
    print(f"📁 Datei: {file}")
    print()

    # Datei-Informationen
    if os.path.exists(file):
        size_mb = os.path.getsize(file) / (1024 * 1024)
        print("📊 Datei-Infos:")
        print(f"   Größe: {size_mb:.1f} MB")
        print(f"   Pfad: {os.path.abspath(file)}")
        print()
        print("✅ Die Datei ist bereit zur Analyse!")

except Exception as e:
    print(f"❌ Fehler beim Download: {e}")
    print()
    print("💡 Tipp: Stelle sicher, dass du 'huggingface_hub' installiert hast:")
    print("   pip install huggingface_hub")

print("=" * 60)

