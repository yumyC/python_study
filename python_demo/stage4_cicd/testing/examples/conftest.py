"""
共享的测试 Fixtures

这个文件中的 fixtures 可以被所有测试文件使用
"""

import pytest
from blog_app import BlogDatabase, BlogService


@pytest.fixture
def clean_database():
    """提供一个干净的数据库实例"""
    return BlogDatabase()


@pytest.fixture
def blog_service(clean_database):
    """提供博客服务实例"""
    return BlogService(clean_database)


@pytest.fixture
def sample_user(blog_service):
    """创建一个示例用户"""
    return blog_service.register_user(
        "sampleuser",
        "sample@example.com",
        "password123"
    )


@pytest.fixture
def sample_post(blog_service, sample_user):
    """创建一个示例文章"""
    return blog_service.create_post(
        sample_user["id"],
        "Sample Post Title",
        "This is a sample post content for testing purposes."
    )


@pytest.fixture
def published_post(blog_service, sample_user, sample_post):
    """创建一个已发布的文章"""
    return blog_service.publish_post(sample_post["id"], sample_user["id"])


@pytest.fixture
def multiple_users(blog_service):
    """创建多个用户"""
    users = []
    for i in range(3):
        user = blog_service.register_user(
            f"user{i}",
            f"user{i}@example.com",
            "password123"
        )
        users.append(user)
    return users


@pytest.fixture
def multiple_posts(blog_service, sample_user):
    """创建多篇文章"""
    posts = []
    for i in range(5):
        post = blog_service.create_post(
            sample_user["id"],
            f"Post {i} Title",
            f"This is the content of post {i}."
        )
        posts.append(post)
    return posts


# 配置 pytest
def pytest_configure(config):
    """pytest 配置"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
