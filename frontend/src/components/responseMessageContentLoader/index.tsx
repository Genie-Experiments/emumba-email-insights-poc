import { Spin } from "antd";
import React, { useEffect, useState } from "react";
import "./styles.css";

interface ResponseMessageContentLoaderProps {
  loading: boolean;
}

const ResponseMessageContentLoader: React.FC<
  ResponseMessageContentLoaderProps
> = ({ loading }) => {
  const [messageIndex, setMessageIndex] = useState(0);
  const [timings, setTimings] = useState<number[]>([]);

  const messages = [
    "Generating Tokens",
    "Creating Embeddings",
    "Gathering Subquestion Context",
    "Passing Through LLM",
    "AI is thinking",
  ];

  // Function to generate random timings that sum to 10 seconds
  const generateRandomTimings = (totalTime: number, count: number) => {
    const times: number[] = [];
    let remainingTime = totalTime;

    for (let i = 0; i < count - 1; i++) {
      const randomTime = Math.random() * (remainingTime / (count - i));
      times.push(randomTime);
      remainingTime -= randomTime;
    }

    times.push(remainingTime); // Push the remaining time for the last message
    return times;
  };

  useEffect(() => {
    if (loading) {
      // Generate random timings summing up to 10 seconds (10,000 ms)
      const randomTimings = generateRandomTimings(13000, messages.length);
      setTimings(randomTimings);
    }
  }, [loading]);

  useEffect(() => {
    let timeoutId: number;
    let totalElapsedTime = 0;

    if (loading && timings.length > 0) {
      const updateMessage = (index: number) => {
        if (index < messages.length) {
          timeoutId = setTimeout(() => {
            setMessageIndex(index);
            totalElapsedTime += timings[index];
            updateMessage(index + 1);
          }, timings[index]);
        }
      };

      updateMessage(0);
    }

    // Clear the timeout when loading finishes or component unmounts
    return () => clearTimeout(timeoutId);
  }, [loading, timings]);

  return (
    <div className="response-message-content-loader">
      <div className="response-content">
        {loading ? (
          <>
            <Spin />
            <p>{messages[messageIndex]} ...</p>
          </>
        ) : (
          <p>Waiting For Your Query</p>
        )}
      </div>
    </div>
  );
};

export default ResponseMessageContentLoader;
