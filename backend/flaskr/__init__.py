from calendar import c
import os
from turtle import title
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers','GET,POST,PATCH,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """        
    @app.route('/categories',methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            
            categoriesList = {} 
            for list in categories:
                categoriesList[list.id] = list.type
                
            return jsonify({
                'success':True,
                'categories': categoriesList
            })
        except:
            abort(405)


    """
    export FLASK_APP=flaskr
    export FLASK_ENV=development
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions',methods=['GET'])
    def get_questions():
        page = request.args.get('page',1,type=int)
        start = (page - 1) * 10
        end = start + 10
        try:
            questions = Question.query.all()    
            categories = Category.query.all()   
            categoriesList = {} 
            for list in categories:
                categoriesList[list.id] = list.type

            format_questions = [question.format() for question in questions ]
            format_categories = [category.format() for category in categories ]
            if(len(format_questions[start:end])==0):
                abort(404)
            return jsonify({
                'success':True,
                'questions': format_questions[start:end],
                'totalQuestions':len(format_questions),
                'categories': categoriesList
            })
        except:
            abort(400)
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()
            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'id': id
            })

        except:
            abort(404)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions',methods=['POST'])
    def add_questions():
        try:
            body = request.get_json()
            question = body.get('question', None)
            answer = body.get('answer', None)
            difficulty = body.get('difficulty', None)
            category = body.get('category', None)
            questions = Question(question=question,answer=answer,category=category,difficulty=difficulty)
            questions.insert()
            return jsonify({
                'success':True
            })
        except:
            abort(400)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search',methods=['POST'])
    def search_questions():
            body = request.get_json()
            searchTerm = body.get('searchTerm', None)
            questions = Question.query.filter(Question.question.ilike('%'+searchTerm+'%')).all()
            format_questions = [question.format() for question in questions ]
            if(len(format_questions) == 0):
                abort(404)
            return jsonify({
                'success':True,
                'questions': format_questions,
                'totalQuestions': len(format_questions),
            })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<category_id>/questions',methods=['GET'])
    def get_categories_question(category_id): 
        try:
            questions = Question.query.filter_by(category=category_id).all()
            category = Category.query.filter_by(id=category_id).one_or_none()
            if category is None:
                abort(404)
            format_questions = [question.format() for question in questions ]
            return jsonify({
                'success':True,
                'questions':format_questions ,
                'totalQuestions':len(format_questions),
                'currentCategory':category.type
            })
        except:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes',methods=['POST'])
    def quizzes():
        try:
            body = request.get_json()
            quiz_category = body.get('quiz_category')
            previous_question = body.get('previous_questions')
            if(quiz_category['id'] == 0):
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category = quiz_category['id']).all()
            #index = random.choices([0,len(questions)-1],1)
            question_ids = [question.id for question in questions]
            #print(question_ids)
            
            #print(index[0])
            if len(question_ids) > len(previous_question):
                index = random.choices([num for num in question_ids if num not in previous_question])
            else:
                index = None
            if(quiz_category['id'] == 0):
                next_question = Question.query.filter_by(id = index[0]).first()
            else:
                if index is not None:
                    next_question = Question.query.filter_by(id = index[0],category = quiz_category['id']).first()
                    #print(next_question)
            
            if index is None:
                return jsonify({})
            else:
                questionList = {                            
                    "answer": next_question.answer,
                    "category": next_question.category,
                    "difficulty": next_question.difficulty,
                    "id": next_question.id,
                    "question": next_question.question
                }
                return jsonify({
                    'success':True,
                    'question': questionList,
                    'previousQuestion': previous_question
                })
        except:
            abort(500)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Page not found"
        }),404
        
    @app.errorhandler(405)
    def page_not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }),405
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }),400

    @app.errorhandler(422)
    def unprocessable_resource(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable resource"
        }),422
        
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500
    return app

