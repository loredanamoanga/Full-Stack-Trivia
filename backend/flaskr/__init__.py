import os
from http.client import HTTPException

import flask
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

__all__ = [setup_db, Question, Category]

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, questions_list):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in questions_list]
    paginated_questions = questions[start:end]
    return paginated_questions


def get_category_list():
    categories = {}
    for category in Category.query.all():
        categories[category.id] = category.type
    return categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        return jsonify({
            'success': True,
            'categories': get_category_list(),
        })

    @app.route('/questions', methods=['GET', 'POST'])
    def get_questions():
        questions_list = Question.query.all()
        paginated_questions = paginate_questions(request, questions_list)
        if len(paginated_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions_list),
            'categories': get_category_list()
        })

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
  
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            questions_list = Question.query.all()
            paginated_questions = paginate_questions(request, questions_list)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': paginated_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category,
                                difficulty=new_difficulty,
                                )
            question.insert()
            questions_list = Question.query.all()
            paginated_questions = paginate_questions(request, questions_list)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': paginated_questions,
                'total_questions': len(Question.query.all())
            })

        except:
            abort(422)

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
  
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''

    @app.route('/questions/query', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        try:
            questions_list = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            paginated_questions = paginate_questions(request, questions_list)

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
  
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            questions_list = Question.query.filter(Question.category == category_id).all()
            paginated_questions = paginate_questions(request, questions_list)

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
  
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    return app
