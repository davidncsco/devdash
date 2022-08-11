import React, { useEffect, useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import ky from 'ky';
import AnimatedChoiceButtons from '../components/styles/Button.styled'
import ProgressBar from '../components/ProgressBar';
import useSound from 'use-sound'
import fanFare from '../Assets/fanfare.mp3'

// More Material UI examples
// https://react.school/material-ui/templates
import {
  makeStyles,
} from "@material-ui/core/styles";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import Container from "@material-ui/core/Container";
import Dialog from "@material-ui/core/Dialog";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";

const useStyles = makeStyles((theme) => ({
  margin: {
    "& > *": {
      margin: theme.spacing(1)
    }
  },
  spacer: {
    marginBottom: theme.spacing(10)
  }
}));

const StyledImage = styled.img`
    width: 1200px;
    height: 650px;
    object-fit: full-width;
`;

const FINISH_LINE = 10

// Virtual Event env var for Sandbox Virtual Event
const VIRTUAL_EVENT = `${process.env.REACT_APP_VIRTUAL_EVENT}`

const Challenge = () => {
    const classes = useStyles();
    const navigate = useNavigate();
    const [answer,setYourAnswer] = useState();
    const [dialogTitle,setDialogTitle] = useState('')
    const [qindex,setQIndex] = useState(1)
    const [openDialog,setOpenDialog] = useState(false)
    const [endofChallenge,setEndOfChallenge] = useState(false)
    const [wrongs, setWrongs] = useState(0)
    const [wrongs2, setWrongs2] = useState(0)
    const [rights, setRights] = useState(0)
    const [completed,setCompleted] = useState(0)
    const [userRank,setUserRank] = useState({"ranked":0,"timetaken":0})
    const [play] = useSound(fanFare);
    const mountedRef = useRef(true);

    // Information passing from registration page
    let location = useLocation()
    let firstname = undefined
    let email     = undefined
    let userid    = undefined
    let greeting  = undefined
    let car       = undefined
    let user      = undefined
    let current_car_position = 0

    if( VIRTUAL_EVENT === 'true' ) {
      user = location.state.user
      firstname = user.first
      email     = user.email
      userid    = location.state.userid
      greeting  = `Welcome to DevRel500 challenge ${firstname}`
    } else {
      car       = location.state.car
      email     = location.state.email
      firstname = location.state.first
      userid    = location.state.userid
      console.log(car)
      greeting = `Welcome to DevRel500 challenge ${firstname} - You've been assigned to the "${car.color}" flag car`
    }
    const questions = location.state.questions
    const [question,setNextQuestion] = useState(questions[qindex-1]);

    // This is used for displaying cars simulation on screen (i.e. need to complete CarRace component)
    function saveCarPositionInLocalStorage(distance) {
        //console.log('Save car positon to localStorage, distance=',distance)
        // If new position negative then reset it to 0
        car.position = ((car.position+distance) >= 0)? car.position+distance : 0
        //console.log('Current car position',car.position)
        //let car_position = {"number": car.number, "position": car.position}
        //localStorage.setItem("car",JSON.stringify(car_position))
    }

    async function sendCommandToCar(car,distance) {
      if( VIRTUAL_EVENT !== 'true' ) {
        console.log('Send KY command to car for user',car.number,'with distance',distance)
        const url = `${process.env.REACT_APP_API_URL}/score?carid=${car.number}&weight=${distance}`
        console.log(url)
        try {
          const json = await ky.put(url)
          console.log( json )
        } catch(error) {
          alert(`Can't send command to car ${car.number} error=${error}, please notify admin`)
        }
        saveCarPositionInLocalStorage(distance)
      }
    }

    async function recordUserTime() {
      console.log('Recording user time...')
      const route = (VIRTUAL_EVENT === 'true') ? `endvirtual?userid=${userid}` : `end?userid=${userid}&carid=${car.number}`
      const url   = `${process.env.REACT_APP_API_URL}/${route}`
      console.log(url)
      try {
        const json = await ky.put(url)
        console.log( json )
      } catch(error) {
        alert(`Can't record user time in database for user ${userid} ${error}, please notify admin`)
      }
    }

    async function resetCar() {
      if (VIRTUAL_EVENT !== 'true') {
        //console.log('Reset car')
        const url = `${process.env.REACT_APP_API_URL}/reset/${car.number}`
        console.log(url)
        try {
          await ky.post(url,{timeout: 25000})
        } catch(error) {
          alert(`Can't reset car# ${car.number} ${error}, please notify admin`)
        }
      }
    }

    async function userRanking() {
      //console.log('Get User Ranking for user with email',email)
      const url = `${process.env.REACT_APP_API_URL}/rank/${email}`
      console.log(url)
      try {
        const json = await ky.get(url).json()
        setUserRank(json)
        console.log(json)
      } catch(error) {
        alert(`Can't get user ranking for user with email ${email} ${error}, please notify admin`)
      }
    }

    useEffect( () => {
      //console.log('Enter userEffect...qindex=',qindex,'answer=',answer)
      if( answer !== undefined ) {    // answer is right or wrong
        setOpenDialog(true)

        if( rights - wrongs > 0 ) {
          current_car_position = rights - wrongs
          console.log('Current position',current_car_position)
          setCompleted( rights - wrongs )
        }
        if( answer && qindex === questions.length ){
          stopTheChallenge()
          return () => { mountedRef.current = false }
        }
      }
    }, [answer,qindex]);

    useEffect( () => {
      //console.log('Enter useEffect for openDialog',openDialog,answer)
      if( (answer !== undefined) && (qindex < questions.length) ) {
          // Compute distance to go back/forth for the car
          let distance = (answer ? 1: -1)
          if( current_car_position >= 0 ) {
            sendCommandToCar(car,distance)
            console.log('Current position in loop',current_car_position)
            console.log('rights',rights, 'wrongs',wrongs)
            setCompleted( rights - wrongs )
          }
      }
    }, [openDialog])
    
    async function stopTheChallenge() {
      console.log('!!! End of Challenge !!!')
      setEndOfChallenge(true)
      play()
      await recordUserTime()
      await userRanking()
      await resetCar()
    }

    async function handleOnEndOfGame() {
      navigate("/",{state:{}})
    }

    function handleOnclick(choice) {    
        //console.log('Enter handleOnClick...qindex:',qindex,'answer',answer)
        let result = question.answer.includes(choice)
        setDialogTitle(result ? 'That is correct!' : 'Incorrect!!!')
        if ( !result ) {
            if( rights - wrongs > 0 || VIRTUAL_EVENT === 'true' )
               setWrongs(wrongs+1)
            else
               setWrongs2(wrongs2+1)  // wrongs2 record # wrong answers when the car is at position 0
        } else {
          setRights(rights+1)
        }
        setOpenDialog(true)
        setYourAnswer(result)
    }

    function handleNextQuestion() {
      //console.log('Enter handleNextQuestion...qindex:',qindex,'answer',answer)
      setOpenDialog(false)
      if( (rights - wrongs) === FINISH_LINE ) {
          setOpenDialog(true)
          stopTheChallenge()
      } else if ( answer && qindex < questions.length ) {
          //console.log('Index increment, set next question...')
          setNextQuestion(questions[qindex])
          setQIndex(qindex+1)
      }
      setYourAnswer(undefined)
    }

    return (
        <Container>
            <Typography color="textSecondary" variant="h6">
                {greeting}
            </Typography>
            <Container >
                <StyledImage src={`/static/questions/${question.filename}`} alt="" id="img" className="img" />
            </Container>
            <Container className={classes.margin}>
                <Typography variant="h6">
                    Please select your answer
                </Typography>
                {question.choices.map((choice) => (
                    <AnimatedChoiceButtons id={choice} variant="contained" key={choice} onClick={() => handleOnclick(choice)}>
                    {choice}
                    </AnimatedChoiceButtons>
                ))}
                <ProgressBar bgcolor={"#6a1b9a"} completed={Math.floor(completed/FINISH_LINE * 100)}/>
                {(openDialog) && (qindex <= questions.length) && (
                    <Dialog open={openDialog}>
                      <DialogTitle>{dialogTitle}</DialogTitle>
                      <DialogContent>
                        <DialogContentText>
                          Click next to continue
                        </DialogContentText>
                      </DialogContent>
                      <DialogActions>
                        <Button onClick={handleNextQuestion} color="secondary" autoFocus>
                          Next
                        </Button>
                      </DialogActions>
                    </Dialog>
                )}
                {openDialog && endofChallenge && (
                  <Dialog open={openDialog}>
                    <DialogTitle><span style={{color: 'red'}}>!!! CONGRATULATIONS !!!</span></DialogTitle>
                    <DialogContent>
                      <DialogContentText>
                        You have crossed the finish line in {userRank.timetaken} seconds. Among {qindex} questions, you answered {wrongs+wrongs2} time(s)
                        incorrectly.  Currently, you're ranked# {userRank.ranked} on the leaderboard.
                        Please click on the trumpet to end the challenge!
                      </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                      <button onClick={handleOnEndOfGame} color="lightblue" autoFocus>
                        <span role="img" aria-label="trumpet">
                          🎺
                        </span>                                                  
                      </button>
                    </DialogActions>
                  </Dialog>
                )}
            </Container>
        </Container>
    );
}

export default Challenge;