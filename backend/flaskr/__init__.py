import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from . import validator

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  RECORDS_PER_PAGE = 10

  cors = CORS(app, resources={r"/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    """ configuring CORS"""
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  def paginate(page, records):
    """ return paginated questions """
    start = (page - 1) * RECORDS_PER_PAGE
    end = start + RECORDS_PER_PAGE
    allRecords = []

    for record, category in records:
      record = record.format()
      record['category_id'] = record['category']
      record['category'] = category
      allRecords.append(record)

    current_records = allRecords[start:end]

    return current_records

  @app.route('/categories')
  def category():
    """ Handle querying categories """
    results = []
    for item in Category.query.all():
      results.append(item.type)
    return jsonify({'categories':results}), 200

  @app.route('/questions')
  def get_questions():
    """ Handle querying questions """
    page = request.args.get('page', 1, type=int)
    questions = Question.query.join(Category,
      Category.id == Question.category).add_columns(Category.type).all()
    current_questions = paginate(page, questions)

    categories = []
    for item in Category.query.all():
      categories.append(item.type)

    if len(current_questions) == 0:
      abort(404)
    
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': categories,
      'current_category': None
    }), 200

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    """ Handle deleteting a question"""
    question = Question.query.filter_by(id=id).first()

    if not question:
      abort(404, "Question not found")
    question.delete()

    return jsonify({
      'success': True,
      'message': 'Question Successfully deleted.'
    }), 200

  @app.route('/questions', methods=['POST'])
  def create_question():
    """ Handle creating a new question"""
    body = request.get_json()
    new_question = Question(
      question = body.get("question"),
      answer = body.get("answer"),
      category = int(body.get("category")),
      difficulty = int(body.get("difficulty"))
    )

    is_valid = validator.question(new_question)

    if not (is_valid == True):
      abort(400, is_valid)

    new_question.insert()
    return jsonify({
      'success': True,
      'message': 'Question Successfully added.'
    }), 200

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    """ Handle searching questions """
    search_term = request.get_json().get("search_term")
    page = request.args.get('page', 1, type=int)
    questions = Question.query.filter(Question.question.contains(search_term)).join(Category,
      Category.id == Question.category).add_columns(Category.type).all()
    current_questions = paginate(page, questions)

    if len(current_questions) == 0:
      abort(404, "No match found.")

    categories = []
    for item in Category.query.all():
      categories.append(item.type)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': categories,
      'current_category': None
    }), 200

  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    """ Handle querying questions by cartegory"""
    page = request.args.get('page', 1, type=int)
    questions = Question.query.filter_by(category=id).join(Category,
      Category.id == Question.category).add_columns(Category.type).all()
    current_questions = paginate(page, questions)

    if len(current_questions) == 0:
      abort(404, "Not found.")

    category = Category.query.filter_by(id=id).first()
    categories = []
    for item in Category.query.all():
      categories.append(item.type)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': categories,
      'current_category': category.type
    }), 200

  @app.route('/quizzes', methods=['POST'])
  def get_quiz_questions():
    """ Handle querying a random quiz question"""
    body = request.get_json()
    questions = Question.query.filter_by(category=body.get('quiz_category')['id']
      ).filter(Question.id.notin_(body.get('previous_questions'))).all()

    if body.get('quiz_category')['id'] == 0:
      questions = Question.query.filter(Question.id.notin_(body.get('previous_questions'))).all()

    if not questions:
      abort(404, "No questions to select from.")
    
    return jsonify({
      'success': True,
      'question': random.choice(questions).format()
    }), 200

  @app.errorhandler(400)
  def custom400(error):
    response = jsonify({
      'message': error.description
      })
    return response, 400

  @app.errorhandler(404)
  def custom404(error):
    response = jsonify({
      'message': error.description
      })
    return response, 404

  @app.errorhandler(422)
  def custom422(error):
    response = jsonify({
      'message': error.description
      })
    return response, 422

  @app.errorhandler(405)
  def custom405(error):
    response = jsonify({
      'message': 'Method not allowed.'
      })
    return response, 405

  return app

    