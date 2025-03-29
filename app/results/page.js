"use client";

import React from 'react'
import { useRouter, useSearchParams } from "next/navigation"
import { useState, useEffect } from "react"
import Result from '../components/Result';

const SecondPage = () => {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState("");

    const searchParams = useSearchParams();
    const request = searchParams.get("request");
    const location = searchParams.get("location");
    const category = searchParams.get("category")

    useEffect(() => {
        if (!request || !location) return;

        const fetchResults = async () => {
            setLoading(true);
            try {
                const response = await fetch(`http://localhost:5000/api/reddit?query=${request}&location=${location}`);
                const data = await response.json();
                setResults(data);
            } catch (error) {
                console.log("Error occurred.");
            } finally {
                setLoading(false);
            }
        };

        fetchResults();
    }, [request, location]);

    if (loading) return <p>Loading recommendations...</p>;
    if (results.length === 0) return <p>No recommendations found.</p>;

    return (
        <div className="container text-center">
            <h1 className="text-2xl py-10">Results for best: <span className="text-red-500 font-semibold">{request} near {location}...</span></h1>
            <p>{JSON.stringify(results)}</p>
            <Result/>
            <Result/>
            <Result/>
        </div>
    )
}

export default SecondPage