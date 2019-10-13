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
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response

  @app.route('/categories')
  def category():
      results = []
      for item in Category.query.all():
        results.append(item.type)
      return jsonify({'categories':results}), 200

  def paginate(page, records):
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

  '''
  @TODO:
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
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

  '''
  @TODO:
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.filter_by(id=id).first()

    if not question:
      abort(404, "Question not found")
    question.delete()

    return jsonify({
      'success': True,
      'message': 'Question Successfully deleted.'
    }), 200

  '''
  @TODO: 
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
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

  '''
  @TODO:
  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search_term = request.get_json().get("search_term")
    page = request.args.get('page', 1, type=int)
    questions = Question.query.filter(Question.question.contains(search_term)).join(Category,
      Category.id == Question.category).add_columns(Category.type).all()
    current_questions = paginate(page, questions)

    if len(current_questions) == 0:
      abort(404, "No match found")

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

  '''
  @TODO: 
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    page = request.args.get('page', 1, type=int)
    questions = Question.query.filter_by(category=id).join(Category,
      Category.id == Question.category).add_columns(Category.type).all()
    current_questions = paginate(page, questions)

    if len(current_questions) == 0:
      abort(404, "Not found")

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

  '''
  @TODO:
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def get_quiz_questions():
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
    return response, 422

  return app

    