import React from 'react';
//These images are event specific. Create a separate directory for each event
import eventLogo from '../Assets/impact22/left-logo.png';
import rightLogo from '../Assets/impact22/blank.png';
import devDash from '../Assets/devdash.png';

import { AppBar, Toolbar, Box, makeStyles } from '@material-ui/core';


const useStyles = makeStyles({
    logo: {
      width: 195,
      height: 40
    },
    dash: {
        width: 150,
        height: 35
    }
  });

const Header = () => {
    const classes = useStyles();

    return (
        <AppBar position="static" color="primary">
            <Toolbar display="flex" p={1}>
                <Box p={1} flexGrow={2} alignSelf="flex-start">
                    <img className={classes.logo} alt="CiscoLive" src={eventLogo} />
                </Box>
                <Box p={1} flexGrow={2} alignSelf="center">
                    <img className={classes.dash} alt="DevDash" src={devDash}/>
                </Box>
                <Box p={1} flexGrow={0} alignSelf="flex-end">
                    <img className={classes.logo} alt="AllIn" src={rightLogo} />
                </Box>
            </Toolbar>
        </AppBar>
    )
}

export default Header