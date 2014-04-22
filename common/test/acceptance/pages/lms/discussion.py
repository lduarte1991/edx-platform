from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise

from .course_page import CoursePage


class DiscussionThreadPage(PageObject):
    url = None

    def __init__(self, browser, thread_selector):
        super(DiscussionThreadPage, self).__init__(browser)
        self.thread_selector = thread_selector

    def _find_within(self, selector):
        """
        Returns a query corresponding to the given CSS selector within the scope
        of this thread page
        """
        return self.q(css=self.thread_selector + " " + selector)

    def is_browser_on_page(self):
        return self.q(css=self.thread_selector).present

    def _get_element_text(self, selector):
        """
        Returns the text of the first element matching the given selector, or
        None if no such element exists
        """
        text_list = self._find_within(selector).text
        return text_list[0] if text_list else None

    def _is_element_visible(self, selector):
        query = self._find_within(selector)
        return query.present and query.visible

    def get_response_total_text(self):
        """Returns the response count text, or None if not present"""
        return self._get_element_text(".response-count")

    def get_num_displayed_responses(self):
        """Returns the number of responses actually rendered"""
        return len(self._find_within(".discussion-response"))

    def get_shown_responses_text(self):
        """Returns the shown response count text, or None if not present"""
        return self._get_element_text(".response-display-count")

    def get_load_responses_button_text(self):
        """Returns the load more responses button text, or None if not present"""
        return self._get_element_text(".load-response-button")

    def load_more_responses(self):
        """Clicks the load more responses button and waits for responses to load"""
        self._find_within(".load-response-button").click()

        def _is_ajax_finished():
            return self.browser.execute_script("return jQuery.active") == 0

        EmptyPromise(
            _is_ajax_finished,
            "Loading more Responses"
        ).fulfill()

    def has_add_response_button(self):
        """Returns true if the add response button is visible, false otherwise"""
        return self._is_element_visible(".add-response-btn")

    def click_add_response_button(self):
        """
        Clicks the add response button and ensures that the response text
        field receives focus
        """
        self._find_within(".add-response-btn").first.click()
        EmptyPromise(
            lambda: self._find_within(".discussion-reply-new textarea:focus").present,
            "Response field received focus"
        ).fulfill()

    def is_response_editor_visible(self, response_id):
        """Returns true if the response editor is present, false otherwise"""
        return self._is_element_visible(".response_{} .edit-post-body".format(response_id))

    def start_response_edit(self, response_id):
        """Click the edit button for the response, loading the editing view"""
        self._find_within(".response_{} .discussion-response .action-edit".format(response_id)).first.click()
        EmptyPromise(
            lambda: self.is_response_editor_visible(response_id),
            "Response edit started"
        ).fulfill()

    def is_add_comment_visible(self, response_id):
        """Returns true if the "add comment" form is visible for a response"""
        return self._is_element_visible("#wmd-input-comment-body-{}".format(response_id))

    def is_comment_visible(self, comment_id):
        """Returns true if the comment is viewable onscreen"""
        return self._is_element_visible("#comment_{} .response-body".format(comment_id))

    def get_comment_body(self, comment_id):
        return self._get_element_text("#comment_{} .response-body".format(comment_id))

    def is_comment_deletable(self, comment_id):
        """Returns true if the delete comment button is present, false otherwise"""
        return self._is_element_visible("#comment_{} div.action-delete".format(comment_id))

    def delete_comment(self, comment_id):
        with self.handle_alert():
            self._find_within("#comment_{} div.action-delete".format(comment_id)).first.click()
        EmptyPromise(
            lambda: not self.is_comment_visible(comment_id),
            "Deleted comment was removed"
        ).fulfill()

    def is_comment_editable(self, comment_id):
        """Returns true if the edit comment button is present, false otherwise"""
        return self._is_element_visible("#comment_{} .action-edit".format(comment_id))

    def is_comment_editor_visible(self, comment_id):
        """Returns true if the comment editor is present, false otherwise"""
        return self._is_element_visible(".edit-comment-body[data-id='{}']".format(comment_id))

    def _get_comment_editor_value(self, comment_id):
        return self._find_within("#wmd-input-edit-comment-body-{}".format(comment_id)).text[0]

    def start_comment_edit(self, comment_id):
        """Click the edit button for the comment, loading the editing view"""
        old_body = self.get_comment_body(comment_id)
        self._find_within("#comment_{} .action-edit".format(comment_id)).first.click()
        EmptyPromise(
            lambda: (
                self.is_comment_editor_visible(comment_id) and
                not self.is_comment_visible(comment_id) and
                self._get_comment_editor_value(comment_id) == old_body
            ),
            "Comment edit started"
        ).fulfill()

    def set_comment_editor_value(self, comment_id, new_body):
        """Replace the contents of the comment editor"""
        self._find_within("#comment_{} .wmd-input".format(comment_id)).fill(new_body)

    def submit_comment_edit(self, comment_id, new_comment_body):
        """Click the submit button on the comment editor"""
        self._find_within("#comment_{} .post-update".format(comment_id)).first.click()
        EmptyPromise(
            lambda: (
                not self.is_comment_editor_visible(comment_id) and
                self.is_comment_visible(comment_id) and
                self.get_comment_body(comment_id) == new_comment_body
            ),
            "Comment edit succeeded"
        ).fulfill()

    def cancel_comment_edit(self, comment_id, original_body):
        """Click the cancel button on the comment editor"""
        self._find_within("#comment_{} .post-cancel".format(comment_id)).first.click()
        EmptyPromise(
            lambda: (
                not self.is_comment_editor_visible(comment_id) and
                self.is_comment_visible(comment_id) and
                self.get_comment_body(comment_id) == original_body
            ),
            "Comment edit was canceled"
        ).fulfill()


class DiscussionTabSingleThreadPage(CoursePage):
    def __init__(self, browser, course_id, thread_id):
        super(DiscussionTabSingleThreadPage, self).__init__(browser, course_id)
        self.thread_page = DiscussionThreadPage(
            browser,
            "body.discussion .discussion-article[data-id='{thread_id}']".format(thread_id=thread_id)
        )
        self.url_path = "discussion/forum/dummy/threads/" + thread_id

    def is_browser_on_page(self):
        return self.thread_page.is_browser_on_page()

    def __getattr__(self, name):
        return getattr(self.thread_page, name)


class InlineDiscussionPage(PageObject):
    url = None

    def __init__(self, browser, discussion_id):
        super(InlineDiscussionPage, self).__init__(browser)
        self._discussion_selector = (
            "body.courseware .discussion-module[data-discussion-id='{discussion_id}'] ".format(
                discussion_id=discussion_id
            )
        )

    def _find_within(self, selector):
        """
        Returns a query corresponding to the given CSS selector within the scope
        of this discussion page
        """
        return self.q(css=self._discussion_selector + " " + selector)

    def is_browser_on_page(self):
        return self.q(css=self._discussion_selector).present

    def is_discussion_expanded(self):
        return self._find_within(".discussion").present

    def expand_discussion(self):
        """Click the link to expand the discussion"""
        self._find_within(".discussion-show").first.click()
        EmptyPromise(
            self.is_discussion_expanded,
            "Discussion expanded"
        ).fulfill()

    def get_num_displayed_threads(self):
        return len(self._find_within(".discussion-thread"))


class InlineDiscussionThreadPage(DiscussionThreadPage):
    def __init__(self, browser, thread_id):
        super(InlineDiscussionThreadPage, self).__init__(
            browser,
            "body.courseware .discussion-module #thread_{thread_id}".format(thread_id=thread_id)
        )

    def expand(self):
        """Clicks the link to expand the thread"""
        self._find_within(".expand-post").first.click()
        EmptyPromise(
            lambda: bool(self.get_response_total_text()),
            "Thread expanded"
        ).fulfill()


class DiscussionUserProfilePage(CoursePage):
    def __init__(self, browser, course_id, user_id, page=1):
        super(DiscussionUserProfilePage, self).__init__(browser, course_id)
        self.url_path = "discussion/forum/dummy/users/{}?page={}".format(user_id, page)
        self._selector = ''.join([
                'section.discussion-user-threads',
                '[data-user-info*=" \\"id\\": \\"{}\\", "]'.format(user_id),
                '[data-course-id="{}"]'.format(course_id)
            ])
        self.page = page

    # FIXME: DRY
    def is_browser_on_page(self):
        return self.q(css=self._selector).present

    # FIXME: DRY
    def _find_within(self, selector):
        """
        Returns a query corresponding to the given CSS selector within the scope
        of this thread page
        """
        return self.q(css=self._selector + " " + selector)

    # FIXME: DRY
    def _get_element_text(self, selector):
        """
        Returns the text of the first element matching the given selector, or
        None if no such element exists
        """
        text_list = self._find_within(selector).text
        return text_list[0] if text_list else None

    # FIXME: DRY
    def _is_element_visible(self, selector):
        query = self._find_within(selector)
        return query.present and query.visible

    def get_shown_thread_ids(self):
        elems = self.q(css="article.discussion-thread[id*=\"thread_\"]")
        return [elem.get_attribute("id")[7:] for elem in elems]

    def get_pagination_current_page(self):
        return int(self.q(css="nav.discussion-paginator li.current-page").text[0])

    def _check_pager(self, text, page_number=None):
        """
        returns True if 'text' matches the text in any of the pagination elements.  If
        page_number is provided, only return True if the element points to that result
        page.
        """
        elems = self.q(css="a.discussion-pagination[data-page-number]")
        pager_dict = dict((elem.text, int(elem.get_attribute('data-page-number'))) for elem in elems)
        return text in pager_dict and (page_number is None or pager_dict[text] == page_number)

    def get_clickable_pages(self):
        return sorted([
            int(elem.get_attribute('data-page-number'))
            for elem in self.q(css="a.discussion-pagination[data-page-number]")
            if str(elem.text).isdigit()
        ])

    def is_prev_button_shown(self, page_number=None):
        return self._check_pager(u'< Previous', page_number)

    def is_next_button_shown(self, page_number=None):
        return self._check_pager(u'Next >', page_number)

    def click_next_page(self):
        current = self.get_pagination_current_page()
        next = [elem for elem in self.q(css="a.discussion-pagination[data-page-number]") if elem.text == 'Next >']
        next[0].click()
        EmptyPromise(
            lambda: self.get_pagination_current_page() == current + 1,
            "Navigated to next page"
        ).fulfill()

    def click_prev_page(self):
        current = self.get_pagination_current_page()
        prev = [elem for elem in self.q(css="a.discussion-pagination[data-page-number]") if elem.text == '< Previous']
        prev[0].click()
        EmptyPromise(
            lambda: self.get_pagination_current_page() == current - 1,
            "Navigated to previous page"
        ).fulfill()

