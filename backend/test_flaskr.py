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
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["categories"])
        
    #def test_delete_categories(self):
        #res = self.client().delete("/categories")
        #data = json.loads(res.data)
        #self.assertEqual(res.status_code,404)
        #self.assertEqual(data["success"],False)
        
    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["categories"])
        
    def test_error_get_questions(self):
        res = self.client().get("/questions?page=10000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')
        
    def test_delete_questions(self):
        res = self.client().delete("/questions/11")
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        
    def test_error_delete_questions(self):
        res = self.client().delete("/questions/10000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page not found")

    def test_add_questions(self):
        testQuestion = {
            'question': 'Are you fullstack?',
            'answer': 'Yes',
            'difficulty': 1,
            'category': 5
        }
        res = self.client().post("/questions",json=testQuestion)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)

    def test_search_questions(self):
        searchTerm = {
            'searchTerm': 'Are you fullstack?',
        }
        res = self.client().post("/questions/search",json=searchTerm)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        
    def test_error_search_questions(self):
        searchTerm = {
            'searchTerm': 'Are you fullstack or not?',
        }
        res = self.client().post("/questions/search",json=searchTerm)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)
        
    def test_get_category_questions(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        
    def test_error_get_category_questions(self):
        res = self.client().get("/categories/10000/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        
    def test_quizzes(self):
        quiz = {
            'previous_questions': [13],
            'quiz_category': {
                'type': 'Entertainment',
                'id': '3'
            }
        }
        res = self.client().post("/quizzes",json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        
    def test_error_quizzes(self):
        quiz = {
            'previous_questions': [17],
            'quiz_category': {
                'type': 'LKS',
                'id': '0'
            }
        }
        res = self.client().post("/quizzes",json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()