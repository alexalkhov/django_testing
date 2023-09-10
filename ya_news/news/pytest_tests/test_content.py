from http import HTTPStatus
from operator import attrgetter

import pytest
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_order(client, page_home):
    response = client.get(page_home)
    object_list = list(response.context['object_list'])
    sorted_dates = sorted(
        object_list,
        key=lambda news: news.date,
        reverse=True
    )
    assert object_list == sorted_dates


def test_news_count(client, page_home, all_news):
    response = client.get(page_home)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == len(all_news)


def test_comment_order(client, test_comments, page_detail):
    url = page_detail
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    test_comments = list(response.context['object'].comment_set.all())
    sorted_comments = sorted(test_comments, key=attrgetter('created'))
    assert test_comments == sorted_comments


def test_anonymous_client_has_no_form(client, page_detail):
    response = client.get(page_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(page_detail, author_client):
    response = author_client.get(page_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
