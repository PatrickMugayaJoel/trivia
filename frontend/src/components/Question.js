import React, { Component } from 'react';
import '../stylesheets/Question.css';
import {ReactComponent as Art} from '../icons/art.svg';
import {ReactComponent as Entertainment} from '../icons/entertainment.svg';
import {ReactComponent as Geography} from '../icons/geography.svg';
// import {ReactComponent as History} from '../icons/history.svg';
import {ReactComponent as Science} from '../icons/science.svg';
import {ReactComponent as Sports} from '../icons/sports.svg';

class Question extends Component {
  constructor(){
    super();
    this.state = {
      visibleAnswer: false
    }
  }

  icons = [
    <Science className="category" />,
    <Art className="category" />,
    <Geography className="category" />,
    <Geography className="category" />,
    <Entertainment className="category" />,
    <Sports className="category" />
  ]

  flipVisibility() {
    this.setState({visibleAnswer: !this.state.visibleAnswer});
  }

  render() {
    const { question, answer, category, difficulty } = this.props;
    return (
      <div className="Question-holder">
        <div className="Question">{question}</div>
        <div className="Question-status">
          {this.icons[category]}
          <div className="difficulty">Difficulty: {difficulty}</div>
          <img src="delete.png" className="delete" onClick={() => this.props.questionAction('DELETE')}/>
          
        </div>
        <div className="show-answer button"
            onClick={() => this.flipVisibility()}>
            {this.state.visibleAnswer ? 'Hide' : 'Show'} Answer
          </div>
        <div className="answer-holder">
          <span style={{"visibility": this.state.visibleAnswer ? 'visible' : 'hidden'}}>Answer: {answer}</span>
        </div>
      </div>
    );
  }
}

export default Question;
