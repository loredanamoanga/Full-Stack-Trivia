import random

from flask import Flask, request, abort, jsonify
from flask_cors import CORS
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
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        return jsonify({
            'success': True,
            'categories': get_category_list(),
        })

    @app.route('/questions', methods=['GET'])
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

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
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

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json(force=True)
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        try:
            question = Question(question=new_question,
                                answer=new_answer,
                                difficulty=new_difficulty,
                                category=new_category)
            if question is None:
                abort(404)

            question.insert()
            questions = Question.query.all()
            paginated_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'created': question.id,
                'id': question.id,
                'questions': paginated_questions,
                'total_questions': len(paginated_questions)
            })

        except:
            abort(422)

    @app.route('/questions/query', methods=['POST'])
    def search_questions():
        body = request.get_json(force=True)
        search_term = body.get('searchTerm', None)

        try:
            questions_list = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            paginated_questions = paginate_questions(request, questions_list)

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(questions_list)
            })
        except:
            abort(422)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            questions_list = Question.query.filter(
                Question.category == category_id).all()
            paginated_questions = paginate_questions(request, questions_list)

            if questions_list is None:
                abort(404)

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_by_category():
        try:
            body = request.get_json(force=True)
            previous_questions = body.get('previous_questions', [])
            quiz_category = body.get('quiz_category')

            category_id = quiz_category.get('id', 0)

            if quiz_category is None:
                abort(404)

            if category_id == 0:
                questions_list = Question.query.all()
            else:
                questions_list = Question.query.filter(
                    Question.category == category_id).all()

            paginated_questions = paginate_questions(request, questions_list)

            filtered_questions = list(
                filter(
                    lambda question:
                    question.get('id') not in previous_questions,
                    paginated_questions
                )
            )

            filtered_question = random.choice(filtered_questions) \
                if filtered_questions else None

            return jsonify({
                'question': filtered_question,
                'success': True
            })

        except:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    return app
