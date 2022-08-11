import styled from 'styled-components'

const AnimatedChoiceButtons = styled.button`
    width: 75px;
    height:50px;
    padding: 5px 5px;
    font-size: 28px;
    text-align: center;
    line-height: 25px;
    color: rgba(255,255,255,0.9);
    border-radius: 50px;
    background: linear-gradient(-45deg, #FFA63D, #FF3D77, #338AFF, #3CF0C5);
    background-size: 600%;
    animation: anime 16s linear infinite;
    box-shadow: 1px 1px 6px rgb(59, 0, 59), -1px 1px 6px rgb(59, 0, 59);
    margin: 10px;
    opacity: 0.9;

    @keyframes anime {
      0% {
        background-position: 0% 50%
        }
      50%
        {
        background-position: 100% 50%
        }
      100%
        {
      background-position: 0% 50%
        }
      }

      &:hover {
        opacity: 0.9;
        transform: scale(0.98);
      }
`;

export default AnimatedChoiceButtons;