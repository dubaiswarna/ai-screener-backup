"""Extract text from Siga candle patterns.docx"""
try:
    from docx import Document
    
    doc = Document(r"C:\python\MG AI\Siga candle patterns.docx")
    
    print("="*80)
    print("SIGA CANDLE PATTERNS")
    print("="*80)
    print()
    
    for para in doc.paragraphs:
        if para.text.strip():
            print(para.text)
    
    print("="*80)
    
except ImportError:
    print("python-docx not installed. Installing...")
    import subprocess
    subprocess.run(["pip", "install", "python-docx"])
    print("\nPlease run this script again.")
except Exception as e:
    print(f"Error: {e}")

