
import { useRef, useState, useEffect } from "react";
import { faCheck, faTimes, faInfoCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useNavigate } from 'react-router-dom';
import ky from 'ky';
import './Registration.css';
import styled from 'styled-components';

// Regular expression use for input validation
const USER_REGEX = /^[A-z][A-z0-9-_]{1,24}$/;
//const EMAIL_REGEX = /^[A-Za-z0-9]+[._]?[A-Za-z0-9]+[@]\w+[. ]\w{2,3}$/;
const EMAIL_REGEX = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;

// Virtual Event env var for Sandbox Virtual Event
const VIRTUAL_EVENT = `${process.env.REACT_APP_VIRTUAL_EVENT}`

const RegisterRectangle = styled.div`
    width: 400px;
    height: 460px;
    overflow: hidden;
    position: relative;
    box-shadow: -3px 3px 7px #00000075, 3px 3px 7px #00000075, 3px -3px 7px #00000075, -3px -3px 7px #00000075;
    margin: 0px auto;
    margin-top: 20px;
    text-align: center;
    background-attachment: fixed;
    padding: 15px;
`;

const Registration = () => {
    const navigate = useNavigate();
    const userRef = useRef();
    const errRef = useRef();

    const [firstname, setFirstname] = useState('');
    const [validFirstname, setValidFirstname] = useState(false);
    const [firstnameFocus, setFirstnameFocus] = useState(false);
    
    const [lastname, setLastname] = useState('');
    const [validLastname, setValidLastname] = useState(false);
    const [lastnameFocus, setLastnameFocus] = useState(false);

    const [email, setEmail] = useState('');
    const [validEmail, setValidEmail] = useState(false);
    const [emailFocus, setEmailFocus] = useState(false);

    const [errMsg, setErrMsg] = useState('');

    const [userid,setUserId] = useState('');
    const [car,setCar] = useState('');
    const [user,setUser] = useState('');

    useEffect(() => {
        userRef.current.focus();
    }, [])

    useEffect(() => {
        setValidFirstname(USER_REGEX.test(firstname));
    }, [firstname])

    useEffect(() => {
      setValidLastname(USER_REGEX.test(lastname));
    }, [lastname])

    useEffect(() => {
        setValidEmail(EMAIL_REGEX.test(email));
    }, [email])

    useEffect(() => {
        setErrMsg('');
    }, [firstname, lastname, email])

    // Fetch questions from DB
    const [questions,setQuestions] = useState('')

    useEffect(() => {
        //console.log('Calling useEffect to fetch questions')
        const url = `${process.env.REACT_APP_API_URL}/questions`
        async function fetchUrl(url) {
            try {
               const json = await ky.get(url).json()
               console.log('questions fetched=',json.length)
               setQuestions(json)
            } catch( error ) {
                alert( `Can't fetch questions from database ${error}`)
            }
        }
        fetchUrl(url)
        console.log('VIRTUAL_EVENT=',VIRTUAL_EVENT)
    }, []);

    // Wait for response from the (promise) POST before navigate to the new page
    useEffect( () => {
        async function fetchUrl(url,setData) {
            try {
                const json = await ky.put(url).json()
                console.log(json)
                setData(json)
            } catch( error ) {
                alert( `Can't start challenge for user ${userid}, ${error}`)
            }
        }
        //console.log('Calling useEffect to start challenge...')
        if( VIRTUAL_EVENT === 'true') {
            if( userid !== '' && user === '' ) {
                const url = `${process.env.REACT_APP_API_URL}/startvirtual?userid=${userid}`
                console.log(url)
                fetchUrl(url,setUser)
            } else if( user !== '' ) {
                console.log('userid',userid)
                navigate("/challenge",{state:{user:user,userid:userid,questions:questions}})
            }
        } else {
            if( userid !== '' && car === '' ) {
                const url = `${process.env.REACT_APP_API_URL}/start?userid=${userid}`
                console.log(url)
                fetchUrl(url,setCar)
            } else if( car !== '' ) {
                console.log('userid',userid)
                navigate("/challenge",{state:{email:email,first:firstname,userid:userid,car:car,questions:questions}})
            }
        }
    }, [userid, car, user]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        // if button enabled with JS hack
        const v1 = USER_REGEX.test(firstname);
        const v2 = USER_REGEX.test(lastname);
        const v3 = EMAIL_REGEX.test(email);
        if (!v1 || !v2 || !v3) {
            setErrMsg("Invalid Entry");
            return;
        }

        const user = { 
            "email": email,
            "first": firstname,
            "last": lastname
        }
        const url = `${process.env.REACT_APP_API_URL}/user`
        console.log(url)
        console.log(user)
        try {
            const json = await ky.post(url,{json: user}).json()
            console.log(json.id)
            setUserId(json.id)
        } catch (error) {
            alert( `Can't register user to database, user with email ${email} may have arealdy taken the challenge. ${error}`)
            setFirstname('')
            setLastname('')
            setEmail('')
        }

        userRef.current.focus()
    }

    return (
        <RegisterRectangle className="App">
            <p ref={errRef} className={errMsg ? "errmsg" : "offscreen"} aria-live="assertive">{errMsg}</p>
            <h1>User Registration</h1>
            <form onSubmit={handleSubmit}>
                <label htmlFor="firstname">
                    First Name:
                    <FontAwesomeIcon icon={faCheck} className={validFirstname ? "valid" : "hide"} />
                    <FontAwesomeIcon icon={faTimes} className={validFirstname || !firstname ? "hide" : "invalid"} />
                </label>
                <input
                    type="text"
                    id="firstname"
                    ref={userRef}
                    autoComplete="off"
                    onChange={(e) => setFirstname(e.target.value)}
                    value={firstname}
                    required
                    aria-invalid={validFirstname ? "false" : "true"}
                    aria-describedby="uidnote"
                    onFocus={() => setFirstnameFocus(true)}
                    onBlur={()  => setFirstnameFocus(false)}
                />
                <p id="uidnote" className={firstnameFocus && firstname && !validFirstname ? "instructions" : "offscreen"}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    2 to 25 characters.<br />
                    Must begin with a letter.<br />
                    Letters, numbers, underscores, hyphens allowed.
                </p>

                <label htmlFor="lastname">
                    Last Name:
                    <FontAwesomeIcon icon={faCheck} className={validLastname ? "valid" : "hide"} />
                    <FontAwesomeIcon icon={faTimes} className={validLastname || !lastname ? "hide" : "invalid"} />
                </label>
                <input
                    type="text"
                    id="lastname"
                    //{userRef}
                    autoComplete="off"
                    onChange={(e) => setLastname(e.target.value)}
                    value={lastname}
                    required
                    aria-invalid={validLastname ? "false" : "true"}
                    aria-describedby="uidnote"
                    onFocus={() => setLastnameFocus(true)}
                    onBlur={()  => setLastnameFocus(false)}
                />
                <p id="uidnote" className={lastnameFocus && lastname && !validLastname ? "instructions" : "offscreen"}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    2 to 24 characters.<br />
                    Must begin with a letter.<br />
                    Letters, numbers, underscores, hyphens allowed.
                </p>

                <label htmlFor="email">
                    Email:
                    <FontAwesomeIcon icon={faCheck} className={validEmail ? "valid" : "hide"} />
                    <FontAwesomeIcon icon={faTimes} className={validEmail || !email ? "hide" : "invalid"} />
                </label>
                <input
                    type="text"
                    id="email"
                    autoComplete="off"
                    onChange={(e) => setEmail(e.target.value)}
                    value={email}
                    required
                    aria-invalid={validEmail ? "false" : "true"}
                    aria-describedby="emailnote"
                    onFocus={() => setEmailFocus(true)}
                    onBlur={() => setEmailFocus(false)}
                />
                <p id="emailnote" className={emailFocus && !validEmail ? "instructions" : "offscreen"}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    8 to 50 characters.<br />
                    Please enter a valid email address<br />
                </p>
                <button disabled={!validFirstname || !validLastname || !validEmail ? true : false}>Start the challenge</button>
            </form>
        </RegisterRectangle>
    )
}

export default Registration;