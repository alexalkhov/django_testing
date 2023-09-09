from http import HTTPStatus
from operator import attrgetter

import pytest

pytestmark = pytest.mark.django_db


def test_news_order(client, page_home):
    response = client.get(page_home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


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
