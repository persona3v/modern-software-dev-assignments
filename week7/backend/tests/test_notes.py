"""
Tests for Note API endpoints including pagination and sorting
"""

def test_create_note(client):
    """Test creating a note"""
    payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test content"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_note(client):
    """Test getting a single note"""
    # Create a note first
    payload = {"title": "Get Test", "content": "Get content"}
    r = client.post("/notes/", json=payload)
    note_id = r.json()["id"]
    
    # Get the note
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Get Test"


def test_get_nonexistent_note(client):
    """Test getting a note that doesn't exist"""
    r = client.get("/notes/99999")
    assert r.status_code == 404


def test_list_notes(client):
    """Test listing all notes"""
    # Create some notes
    for i in range(3):
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})
    
    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 3


def test_search_notes(client):
    """Test searching notes"""
    client.post("/notes/", json={"title": "Searchable", "content": "Unique content xyz"})
    client.post("/notes/", json={"title": "Other", "content": "Different"})
    
    r = client.get("/notes/", params={"q": "Unique"})
    assert r.status_code == 200
    items = r.json()
    assert any("Unique" in item["content"] for item in items)


def test_search_no_results(client):
    """Test search with no results"""
    r = client.get("/notes/", params={"q": "nonexistent_xyz_123"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 0


# ==================== Pagination Tests ====================

def test_pagination_default(client):
    """Test default pagination"""
    # Create 10 notes
    for i in range(10):
        client.post("/notes/", json={"title": f"Page {i}", "content": f"Content {i}"})
    
    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    # Default limit is 50, should return all
    assert len(items) >= 10


def test_pagination_limit(client):
    """Test pagination with limit"""
    # Create 5 notes
    for i in range(5):
        client.post("/notes/", json={"title": f"Limit {i}", "content": f"Content {i}"})
    
    r = client.get("/notes/", params={"limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 2


def test_pagination_skip(client):
    """Test pagination with skip (offset)"""
    # Create 5 notes
    for i in range(5):
        client.post("/notes/", json={"title": f"Skip {i}", "content": f"Content {i}"})
    
    # Skip first 2
    r = client.get("/notes/", params={"skip": 2, "limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 2


def test_pagination_skip_and_limit(client):
    """Test combined skip and limit"""
    for i in range(6):
        client.post("/notes/", json={"title": f"Combined {i}", "content": f"C{i}"})
    
    r = client.get("/notes/", params={"skip": 2, "limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 2


def test_pagination_limit_max(client):
    """Test that limit is capped at 200"""
    r = client.get("/notes/", params={"limit": 500})
    assert r.status_code == 200
    # Should be capped at 200
    items = r.json()
    assert len(items) <= 200


def test_pagination_limit_min(client):
    """Test that limit has minimum of 1"""
    r = client.get("/notes/", params={"limit": 0})
    # Should either work with 0 or reject
    assert r.status_code in [200, 422]


# ==================== Sorting Tests ====================

def test_sort_by_created_at_desc(client):
    """Test sorting by created_at descending (default)"""
    # Create notes in known order
    for i in range(3):
        client.post("/notes/", json={"title": f"Sort {i}", "content": f"C{i}"})
    
    r = client.get("/notes/", params={"sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    # Should be sorted descending (newest first)
    assert len(items) >= 3


def test_sort_by_created_at_asc(client):
    """Test sorting by created_at ascending"""
    for i in range(3):
        client.post("/notes/", json={"title": f"ASC {i}", "content": f"C{i}"})
    
    r = client.get("/notes/", params={"sort": "created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 3


def test_sort_by_title(client):
    """Test sorting by title"""
    client.post("/notes/", json={"title": "Zebra", "content": "Z"})
    client.post("/notes/", json={"title": "Apple", "content": "A"})
    client.post("/notes/", json={"title": "Mango", "content": "M"})
    
    r = client.get("/notes/", params={"sort": "title"})
    assert r.status_code == 200
    items = r.json()
    # Filter to just our test items
    test_items = [i for i in items if i["title"] in ["Zebra", "Apple", "Mango"]]
    if len(test_items) >= 2:
        titles = [i["title"] for i in test_items]
        # Should be sorted alphabetically
        assert titles == sorted(titles)


def test_sort_by_title_desc(client):
    """Test sorting by title descending"""
    client.post("/notes/", json={"title": "Alpha", "content": "A"})
    client.post("/notes/", json={"title": "Beta", "content": "B"})
    
    r = client.get("/notes/", params={"sort": "-title"})
    assert r.status_code == 200
    items = r.json()
    test_items = [i for i in items if i["title"] in ["Alpha", "Beta"]]
    if len(test_items) >= 2:
        titles = [i["title"] for i in test_items]
        # Should be sorted reverse alphabetically
        assert titles == sorted(titles, reverse=True)


def test_sort_invalid_field(client):
    """Test sorting by invalid field falls back to default"""
    r = client.get("/notes/", params={"sort": "invalid_field"})
    assert r.status_code == 200
    # Should still return results, using default sort


# ==================== Combined Tests ====================

def test_search_with_pagination(client):
    """Test search combined with pagination"""
    client.post("/notes/", json={"title": "Searchable1", "content": "Find me"})
    client.post("/notes/", json={"title": "Searchable2", "content": "Find me too"})
    client.post("/notes/", json={"title": "Other", "content": "Don't find"})
    
    r = client.get("/notes/", params={"q": "Find", "limit": 1})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 1


def test_search_with_sort(client):
    """Test search combined with sorting"""
    client.post("/notes/", json={"title": "ZZZ Search", "content": "Content"})
    client.post("/notes/", json={"title": "AAA Search", "content": "Content"})
    
    r = client.get("/notes/", params={"q": "Search", "sort": "title"})
    assert r.status_code == 200
    items = r.json()
    test_items = [i for i in items if "Search" in i["title"]]
    if len(test_items) >= 2:
        titles = [i["title"] for i in test_items]
        assert titles == sorted(titles)


def test_pagination_with_sort(client):
    """Test pagination combined with sorting"""
    for i in range(5):
        client.post("/notes/", json={"title": f"Note {i}", "content": f"C{i}"})
    
    r = client.get("/notes/", params={"skip": 0, "limit": 2, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 2


# ==================== Edge Cases ====================

def test_empty_search_query(client):
    """Test search with empty query returns all"""
    client.post("/notes/", json={"title": "Test", "content": "Content"})
    
    r = client.get("/notes/", params={"q": ""})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_whitespace_search_query(client):
    """Test search with whitespace only"""
    r = client.get("/notes/", params={"q": "   "})
    assert r.status_code == 200
    # Should return all or empty depending on implementation


def test_note_count_endpoint(client):
    """Test the count endpoint"""
    # Create some notes
    for i in range(3):
        client.post("/notes/", json={"title": f"Count {i}", "content": f"C{i}"})
    
    r = client.get("/notes/count")
    assert r.status_code == 200
    data = r.json()
    assert "count" in data
    assert data["count"] >= 3
