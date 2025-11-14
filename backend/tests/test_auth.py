import json

def test_developer_cannot_create_project(client):
    """
    GIVEN a logged-in Developer
    WHEN they attempt to create a project via the API
    THEN they should receive a 403 Forbidden error
    """

    # 1. ARRANGE: Register and login as a Developer
    reg_data = {
        "full_name": "Test Dev for Tests",
        "email": "testdev@test.com",
        "password": "password123",
        "role": "Developer"
    }
    # The 'client' fixture comes from conftest.py
    client.post('/api/register', data=json.dumps(reg_data), content_type='application/json')

    login_data = {
        "email": "testdev@test.com",
        "password": "password123"
    }
    login_res = client.post('/api/login', data=json.dumps(login_data), content_type='application/json')
    token = login_res.json['access_token']

    # 2. ACT: Attempt to create a project
    project_data = {
        "name": "A Project I Can't Make"
    }
    headers = {
        'Authorization': f'Bearer {token}'
    }
    res = client.post('/api/projects', data=json.dumps(project_data), content_type='application/json', headers=headers)

    # 3. ASSERT: Check for 403 Forbidden
    assert res.status_code == 403
    assert res.json['message'] == "You are not authorized to create projects!"