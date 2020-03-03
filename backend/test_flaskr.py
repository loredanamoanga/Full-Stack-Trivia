import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Graffiti comes from the Italian word graffiato, meaning what?',
            'answer': 'scratched',
            'difficulty': 1,
            'category': 2
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client.get('/categories')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)
        self.assertTrue(len(data.get('categories')))

    def test_get_paginated_questions(self):
        res = self.client.get('/questions')
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_422_get_if_question_does_not_exist(self):
        res = self.client.get('/questions/?page=1000')
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_delete_question(self):
        res = self.client.delete('/questions/79')
        data = res.get_json()
        question = Question.query.filter(Question.id == 79).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)

    def test_422_delete_if_question_does_not_exist(self):
        res = self.client.delete('/questions/999')
        data = res.get_json()
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')


    def test_post_new_question(self):

        res = self.client.post("/questions",
                               content_type="application/json",
                               data=json.dumps(self.new_question))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_post_without_new_question(self):
        empty_question = {
            "question": "",
            "answer": "",
            "difficulty": "",
            "category": ""
        }

        res = self.client.post("/questions", content_type="application/json", data=json.dumps(empty_question))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_post_search_term(self):
        search_term = {
            'searchTerm': 'is',
        }
        res = self.client.post("/questions/query",
                               content_type="application/json",
                               data=json.dumps(search_term))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_post_search_without_term(self):
        search_term = {
            'searchTerm': 'thiswillnotbefound',
        }
        res = self.client.post("/questions/query",
                               content_type="application/json",
                               data=json.dumps(search_term)
                               )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertFalse(len(data['questions']))

    def test_get_questions_by_category(self):
        res = self.client.get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_questions_by_category_if_it_does_not_exist(self):
        res = self.client.get('/categories/11111/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_post_quizzes(self):
        test_quiz = {
            'previous_questions': [],
            'quiz_category': {
                'id': 2,
                'type': 'Art'
            }
        }
        res = self.client.post('/quizzes', json=test_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_post_quizzes_without_data(self):
        res = self.client.post('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
