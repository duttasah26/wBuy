"use client";

import React from 'react'
import { useRouter, useSearchParams } from "next/navigation"
import { useState, useEffect } from "react"
import Result from '../components/Result';
import { FaArrowCircleLeft, FaArrowCircleRight } from "react-icons/fa";

const SecondPage = () => {
    const [loading, setLoading] = useState(true);
    const [results, setResults] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0); 
    const [slideDirection, setSlideDirection] = useState(0);

    const searchParams = useSearchParams();
    const request = searchParams.get("request");
    const location = searchParams.get("location");
    const category = searchParams.get("category")

    useEffect(() => {
        if (!request || !location) return;

        const fetchResults = async () => {
            setLoading(true);
            try {
                const response = await fetch(`http://localhost:5000/api/analyze?query=${request}&category=${category}&location=${location}`);
                const data = await response.json();
                setResults(data.recommendations);

            } catch (error) {
                console.log(error);
                setResults([]);
            } finally {
                setLoading(false);
            }
        };

        fetchResults();
    }, [request, location]);

    const handleNext = () => {
        setSlideDirection(1);
        setCurrentIndex((prevIndex) => (prevIndex + 1) % results.length);
    }

    const handlePrevious = () => {
        setSlideDirection(-1);
        setCurrentIndex((prevIndex) => (prevIndex - 1 + results.length) % results.length);
    }

    if (loading) return (
        <p className="text-center py-50">Loading recommendations...</p>
    );

    return (
        <div className="container text-center mx-auto py-4">
            <h1 className="text-2xl py-10">Results for best: <span className="font-semibold">{request} near {location}...</span></h1>
            
            {results.length === 0 ? (
                <p>No recommendations found.</p>
            ) : (
                <div className="flex justify-between items-center space-x-2 mt-4">
                    <FaArrowCircleLeft onClick={handlePrevious} className="h-10 w-10 mr-0 pr-0 hover:text-blue-500 active:scale-110 transition-all duration-300"/>
                    <div className="flex-grow transition-transform duration-500 ease-in-out">
                        <Result
                            key = {currentIndex}
                            name = {results[currentIndex].name}
                            rating = {results[currentIndex].rating}
                            key_features = {results[currentIndex].key_features}
                            quotes = {results[currentIndex].quotes}
                        />
                    </div>
                    <FaArrowCircleRight onClick={handleNext} className="h-10 w-10 mr-0 pr-0 hover:text-blue-500 active:scale-110 transition-all duration-300"/>
                </div>
                )
            }

            {/* Link back to Homepage */}
            <div className="mt-6">
                <a href="/" className="text-blue-500 text-lg hover:underline">Back to Homepage</a>
            </div>
        </div>
    )
}

export default SecondPage