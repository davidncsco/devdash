
import { Button,Container,Grid, Typography } from "@material-ui/core";
import ky from 'ky';

const Instructions = () => {

    async function resetCar(e) {
        const car_number = e.currentTarget.value
        console.log('Send KY command to reset car#',car_number)
        const url = `${process.env.REACT_APP_API_URL}/reset/${car_number}`
        console.log(url)
        try {
          const json = await ky.put(url)
          alert(`Car #${car_number} reset`)
          console.log( json )
        } catch(error) {
          alert(`Can't reset car for car number ${car_number}, ${error}`)
        }
    }

    return (
        <Container>
        <Typography variant="h4" color="textPrimary">
            This page is used to reset car in the database.
            Please do not use if challenge is in progress. Click on button will reset car and make it available for the next user.
            Please make sure to move the car back to the starting position
        </Typography>
        <Grid container
            direction="row"
            justifyContent="space-evenly"
            alignItems="center">
            <Button variant="contained" color="secondary" size="large" onClick={resetCar} value="1">
                Reset Car # 1
            </Button>
            <Button variant="contained" color="secondary" onClick={resetCar} value="2">
                Reset Car # 2
            </Button>
            <Button variant="contained" color="secondary" onClick={resetCar} value="3">
                Reset Car # 3
            </Button>
        </Grid>
        </Container>
    );
}

export default Instructions