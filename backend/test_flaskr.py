import os
import unittest
import json
import random
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.database_name = "trivia_test"
        self.database_path = "postgresql://root:root@{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):

        response  = self.client.get('/categories')

        body = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(body['categories'], list))

    def test_get_questions(self):

        response  = self.client.get('/questions')

        body = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['current_category'], None)

    def test_delete_question(self):
        resp = json.loads(self.client.get('/questions').data.decode())
        count1 = resp['total_questions']
        response  = self.client.delete(f'/questions/{random.choice(resp["questions"])["id"]}')
        count2 = json.loads(self.client.get('/questions').data.decode())['total_questions']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(count1, count2+1)

    def test_post_question(self):
        body = {
            "question": "question",
            "answer": "answer",
            "category": 1,
            "difficulty": 2
        }
        count1 = json.loads(self.client.get('/questions').data.decode())['total_questions']
        response  = self.client.post('/questions',
            content_type='application/json',
            data=json.dumps(body))
        count2 = json.loads(self.client.get('/questions').data.decode())['total_questions']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(count1, count2-1)

    def test_search_questions(self):
        # I choose this search term on assumption that there
        # shall always be a queston starting with "what"
        body = {"search_term": "hat"}
        count1 = json.loads(self.client.get('/questions').data.decode())['total_questions']
        response  = self.client.post('/questions/search',
            content_type='application/json',
            data=json.dumps(body))
        count2 = json.loads(response.data.decode())['total_questions']

        self.assertEqual(response.status_code, 200)
        self.assertTrue((count1 > count2) and (count2 > 0))

    def test_get_questions_by_category(self):
        # I have made an assumption that category with id 1 will always be science
        response  = self.client.get('/categories/1/questions')

        body = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['current_category'], "Science")

    def test_get_quiz_question(self):
        body = {
            "quiz_category": {"type":"", "id":0},
            "previous_questions": []
        }
        response  = self.client.post('/quizzes',
            content_type='application/json',
            data=json.dumps(body))

        body = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(body['question']['question'], str))

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()