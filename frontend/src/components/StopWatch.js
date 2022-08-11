import React, { useState, useEffect } from "react";
import styled from 'styled-components'

const Timer = styled.h3` {
    font-family: 'Rajdhani', sans-serif;
    margin : 1rem;
    width: 100%;
    display: flex;
    height: 12%;
    justify-content: center;
    align-items: center;
}`

const formatTime = (timer) => {
    const getSeconds = `0${(timer % 60)}`.slice(-2)
    const minutes = `${Math.floor(timer / 60)}`
    const getMinutes = `0${minutes % 60}`.slice(-2)
  
    return `${getMinutes} : ${getSeconds}`
  }

const StopWatch = () => {
  const [count, setCount] = useState(0);

  useEffect(() => {
      const timer = setTimeout(() => {
        setCount((prevCount) => prevCount + 1);
      }, 1000);

      return () => {
        clearTimeout(timer);
      };
  });

  return (
    <Timer>
        {formatTime(count)}
    </Timer>
  );
}

export default StopWatch;