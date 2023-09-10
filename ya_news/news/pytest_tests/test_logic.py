from http import HTTPStatus

import pytest
from conftest import COMMENT_TEXT, NEW_COMMENT_TEXT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, page_detail, form_data):
    response = client.post(page_detail, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client,
        page_detail,
        form_data,
        news,
        author
):
    response = author_client.post(page_detail, data=form_data)
    assertRedirects(response, f'{page_detail}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, page_detail):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(page_detail, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(page_detail, author_client, delete_url):
    before = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, page_detail + '#comments')
    assert before != Comment.objects.count()


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND)
    ),
)
def test_users_cant_delete_comment_of_another_user(
    delete_url,
    parametrized_client,
    expected_status
):
    response = parametrized_client.delete(delete_url)
    assert response.status_code == expected_status
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        comment,
        author_client,
        edit_url,
        new_data,
        page_detail
):
    response = author_client.post(edit_url, data=new_data)
    assertRedirects(response, page_detail + '#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        admin_client,
        edit_url,
        new_data,
        comment
):
    response = admin_client.post(edit_url, data=new_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
