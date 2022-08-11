import React from 'react';
import styled from 'styled-components';

const StyledFooter = styled.div`
    bottom: 0;
    padding: 0;
    color: black;
    display: grid;
    place-content: center;
    margin-top: 1rem;
`;

const Footer = () => {
    const today = new Date();

    return (
        <StyledFooter>
            <p>Copyright &copy; {today.getFullYear()} Cisco Systems, Inc.</p>
        </StyledFooter>
    )
}

export default Footer