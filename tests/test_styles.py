"""
Test script for mapping/styles.py
Tests color generation, style configurations, and HTML templates
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mapping.styles import (
    ColorScheme,
    LayerStyles,
    PopupConfig,
    HTMLTemplates,
    MapConfig,
    sanitize_for_html,
    owner_to_slug
)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_color_generation():
    """Test color scheme generation"""
    print_section("TEST 1: Color Generation")
    
    owners = ['SMITH PROPERTIES', 'JONES INVESTMENTS', 'BROWN HOLDINGS']
    
    colors = ColorScheme.generate_owner_colors(owners)
    
    print(f"Generated colors for {len(owners)} owners:")
    for owner, color in colors.items():
        print(f"  {owner}: {color}")
    
    checks = [
        (len(colors) == len(owners), "Generated color for each owner"),
        (all(c.startswith('#') for c in colors.values()), "All colors are hex format"),
        (len(set(colors.values())) == len(owners), "All colors are unique")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Color generation successful")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_layer_styles():
    """Test layer style configurations"""
    print_section("TEST 2: Layer Styles")
    
    base_style = LayerStyles.get_base_style()
    owner_style = LayerStyles.get_owner_style("#ff0000", 0.7)
    zip_style = LayerStyles.get_zip_style("#00ff00", 0.5)
    
    print("Base Context Style:")
    for key, value in base_style.items():
        print(f"  {key}: {value}")
    
    print("\nOwner Style (red, 0.7 opacity):")
    for key, value in owner_style.items():
        print(f"  {key}: {value}")
    
    print("\nZIP Style (green, 0.5 opacity):")
    for key, value in zip_style.items():
        print(f"  {key}: {value}")
    
    checks = [
        (base_style['color'] == 'grey', "Base style has grey color"),
        (owner_style['color'] == '#ff0000', "Owner style uses specified color"),
        (owner_style['fillOpacity'] == 0.7, "Owner style uses specified opacity"),
        (zip_style['fillOpacity'] == 0.5, "ZIP style uses specified opacity"),
        (all('weight' in s for s in [base_style, owner_style, zip_style]), "All styles have weight property")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Layer styles configured correctly")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_popup_config():
    """Test popup field configuration"""
    print_section("TEST 3: Popup Configuration")
    
    # Simulate DataFrame columns
    columns = ['parcelpin', 'par_addr', 'owner_clean', 'sales_amount', 'par_zip', 'other_field']
    
    available_fields = PopupConfig.get_available_fields(columns)
    aliases = PopupConfig.get_aliases(available_fields)
    
    print(f"Available columns: {columns}")
    print(f"\nSelected popup fields: {available_fields}")
    print(f"\nField aliases:")
    for field, alias in zip(available_fields, aliases):
        print(f"  {field} → {alias}")
    
    # Test value formatting
    print(f"\nValue Formatting:")
    test_values = [
        ('sales_amount', 250000, '$250,000'),
        ('parcelpin', '123-456-789', '123-456-789'),
        ('sales_amount', None, 'N/A')
    ]
    
    formatting_correct = True
    for field, value, expected in test_values:
        formatted = PopupConfig.format_value(field, value)
        matches = formatted == expected
        status = "✓" if matches else "✗"
        print(f"  {status} {field}={value} → {formatted} (expected: {expected})")
        if not matches:
            formatting_correct = False
    
    checks = [
        (len(available_fields) > 0, "Found available fields"),
        (len(available_fields) == len(aliases), "Alias count matches field count"),
        ('parcelpin' in available_fields, "Parcelpin field included"),
        ('other_field' not in available_fields, "Non-standard field excluded"),
        (formatting_correct, "Value formatting correct")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Popup configuration working")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_html_templates():
    """Test HTML template generation"""
    print_section("TEST 4: HTML Templates")
    
    # Test sidebar CSS
    css = HTMLTemplates.get_sidebar_css()
    print(f"Sidebar CSS length: {len(css)} characters")
    print("CSS includes:")
    css_elements = ['#gs-sidebar', 'table', 'h2', 'select']
    for element in css_elements:
        exists = element in css
        status = "✓" if exists else "✗"
        print(f"  {status} {element} selector")
    
    # Test stats table HTML
    rows = [
        ('SMITH PROPERTIES', 5, '$1,250,000'),
        ('JONES INVESTMENTS', 3, '$780,000')
    ]
    headers = ['Owner', 'Count', 'Total Sales']
    table_html = HTMLTemplates.get_stats_table_html(rows, headers, "Portfolio Summary")
    
    print(f"\nGenerated stats table ({len(table_html)} chars)")
    print("Table includes:")
    table_elements = ['<table', '<th>', '<td>', 'Portfolio Summary']
    for element in table_elements:
        exists = element in table_html
        status = "✓" if exists else "✗"
        print(f"  {status} {element}")
    
    # Test sidebar template
    sidebar = HTMLTemplates.get_sidebar_template()
    print(f"\nSidebar template ({len(sidebar)} chars)")
    print("Template includes placeholders:")
    placeholders = ['{owner_options}', '{owner_select_options}', '{zip_select_options}', '{stat_panels}']
    for placeholder in placeholders:
        exists = placeholder in sidebar
        status = "✓" if exists else "✗"
        print(f"  {status} {placeholder}")
    
    checks = [
        (len(css) > 500, "CSS has substantial content"),
        (all(el in css for el in css_elements), "CSS has all key selectors"),
        ('<table' in table_html, "Stats table generated"),
        (all(p in sidebar for p in placeholders), "Sidebar has all placeholders"),
        ('Portfolio Viewer' in sidebar, "Sidebar has title")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: HTML templates working")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_map_config():
    """Test map configuration"""
    print_section("TEST 5: Map Configuration")
    
    # Test tile configurations
    print("Available tile layers:")
    for tile_type in ['light', 'dark', 'osm', 'satellite']:
        config = MapConfig.get_tile_config(tile_type)
        print(f"  {tile_type}: {config['name']}")
    
    default_tile = MapConfig.get_tile_config()
    print(f"\nDefault tile: {default_tile['name']}")
    print(f"Default zoom: {MapConfig.DEFAULT_ZOOM}")
    
    # Test layer control config
    layer_control = MapConfig.LAYER_CONTROL
    print(f"\nLayer control settings:")
    for key, value in layer_control.items():
        print(f"  {key}: {value}")
    
    checks = [
        (len(MapConfig.TILE_LAYERS) >= 4, "At least 4 tile layers available"),
        ('tiles' in default_tile, "Tile config has 'tiles' key"),
        ('attr' in default_tile, "Tile config has 'attr' key"),
        (MapConfig.DEFAULT_ZOOM > 0, "Default zoom is positive"),
        ('position' in layer_control, "Layer control has position")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Map configuration working")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_utility_functions():
    """Test utility functions"""
    print_section("TEST 6: Utility Functions")
    
    # Test HTML sanitization
    test_cases = [
        ('<script>alert("XSS")</script>', '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'),
        ('Smith & Jones', 'Smith &amp; Jones'),
        ("It's here", 'It&#x27;s here'),
        ('Normal text', 'Normal text')
    ]
    
    print("HTML Sanitization:")
    sanitize_correct = True
    for input_text, expected in test_cases:
        result = sanitize_for_html(input_text)
        matches = result == expected
        status = "✓" if matches else "✗"
        print(f"  {status} '{input_text}' → '{result}'")
        if not matches:
            print(f"       Expected: '{expected}'")
            sanitize_correct = False
    
    # Test owner slug generation
    print("\nOwner Slug Generation:")
    slug_cases = [
        ('SMITH PROPERTIES', 'owner_smith_properties'),
        ('JONES & CO', 'owner_jones_co'),
        ('BROWN-HOLDINGS LLC', 'owner_brown_holdings_llc')
    ]
    
    slug_correct = True
    for owner, expected in slug_cases:
        result = owner_to_slug(owner)
        matches = result == expected
        status = "✓" if matches else "✗"
        print(f"  {status} '{owner}' → '{result}'")
        if not matches:
            print(f"       Expected: '{expected}'")
            slug_correct = False
    
    checks = [
        (sanitize_correct, "HTML sanitization working"),
        (slug_correct, "Owner slug generation working"),
        (all(sanitize_for_html(t[0]) != t[0] for t in test_cases[:3]), "Sanitization makes changes"),
        (all(owner_to_slug(t[0]).startswith('owner_') for t in slug_cases), "All slugs start with 'owner_'")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Utility functions working")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("  MAP STYLES TEST SUITE")
    print("="*60)
    
    tests = [
        ("Color Generation", test_color_generation),
        ("Layer Styles", test_layer_styles),
        ("Popup Configuration", test_popup_config),
        ("HTML Templates", test_html_templates),
        ("Map Configuration", test_map_config),
        ("Utility Functions", test_utility_functions)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False, str(e)))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"       Error: {error}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Map styles module is working correctly.\n")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review errors above.\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

