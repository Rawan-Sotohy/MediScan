const steps = [
    "Uploading Image",
    "Analyzing Prescription...",
    "Extracting Medicine Names...",
    "Reading Dosages...",
    "Detecting Frequency & Duration...",
    "Preparing Result..."
    ];
let index = 0;
// function changeText ()
// {
//     const text = document.getElementById( "loadingText" );
//     text.innerText = steps[ index ];
//     index++
//     if (index< steps.length )
//     {
//         setTimeout(changeText,1500);
//     } else
//     {
//         window.location.href = "extract.html";
//     }
// }

function upateState()
{
    const step = document.getElementById( "steptext" );
    step.innerText = steps[ index ];
    index++
    if (index< steps.length )
        {
            setTimeout(upateState,1500);
        } else
        {
            window.location.href = "extract.html";
        }
}
    
// changeText();
upateState();