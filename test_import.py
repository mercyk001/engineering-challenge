import sys
print("Python path:")
for path in sys.path:
    print(f"  {path}")

try:
    from models.case import Case
    print("\n Successfully imported Case from models.case")
    
    
    test_case = Case(
        case_id="test_001",
        title="Test Case",
        citation="[2024] eKLR 1",
        court="High Court",
        judges=["Mercy "],
        judgment_date="2024-01-01",
        parties={"plaintiff": ["yooo"], "defendant": ["wueh"]},
        summary="Test summary",
        url="http://test.com",
        pdf_url=None
    )
    print(f"✅ Created case: {test_case.title}")
    
except ImportError as e:
    print(f"\n Import error: {e}")
    print("\n Make sure models/case.py exists")
