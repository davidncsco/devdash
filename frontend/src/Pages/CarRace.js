import React, { useState,useEffect } from "react";

// This is a placeholder template for implementing the virtual race display
// Not fully implemented yet.
const CarRace = () => {
  const now = new Date().toLocaleTimeString();
  let [time, setTime] = useState(now);
  let [positions, setPosition] = useState([1,2,3,4])

  useEffect(() => {
    console.log(`initializing interval`);
    console.log(positions);
    const interval = setInterval(() => {
      updateTime();
    }, 10000);

    return () => {
      console.log(`clearing interval`);
      clearInterval(interval);
    };
  }, []); // has no dependency - this will be called on-component-mount

  function updateTime() {
    console.log('updateTime')
    const newTime = new Date().toLocaleTimeString();
    setTime(newTime);

    const car = JSON.parse(localStorage.getItem("car"))
    console.log('curr',positions)
    positions[car.number-1] = car.position
    console.log('new',positions)
    setPosition(positions)
  }

  function updateFromDB() {
    setPosition([4,3,2,1])
  }

  return (
    <div className="container">
      <h1>{time}</h1>
      <p>Car Position 1: {positions[0]}</p>
      <p>Car Position 2: {positions[1]}</p>
      <p>Car Position 3: {positions[2]}</p>
      <p>Car Position 4: {positions[3]}</p>
      <button onClick={updateFromDB}>DB update</button>
    </div>
  );
}

export default CarRace;