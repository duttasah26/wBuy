"use client";

import React from 'react'
import { useRouter, useSearchParams } from "next/navigation"
import { useState, useEffect } from "react"
import Result from '../components/Result';
import LoadingAnimation from '../components/LoadingAnimation';
import { FaExternalLinkAlt, FaStar, FaList, FaQuoteRight } from 'react-icons/fa';

const SecondPage = () => {
    const [loading, setLoading] = useState(true);
    const [results, setResults] = useState([]);

    const searchParams = useSearchParams();
    const request = searchParams.get("request");
    const location = searchParams.get("location");
    const category = searchParams.get("category");

    useEffect(() => {
        if (!request) return; // Only require the request parameter

        const fetchResults = async () => {
            setLoading(true);
            try {
                let url = `http://localhost:5000/api/analyze?query=${request}&category=${category}`;
                if (location) {
                    url += `&location=${location}`; // Add location only if it exists
                }
                const response = await fetch(url);
                const data = await response.json();
                setResults(data.recommendations || []);
            } catch (error) {
                console.log(error);
                setResults([]);
            } finally {
                setTimeout(() => {
                    setLoading(false);
                }, 1000);
            }
        };

        fetchResults();
    }, [request, location, category]);

    if (loading) return <LoadingAnimation />;

    return (
        <div className="container text-center mx-auto py-4 bg-[#0e2c3b] text-[#f8f0dd] min-h-screen px-4">
        <h1 className="text-3xl py-10 font-bold">
        {category === "product" ? (
            <>Results for best: <span className="text-[#26a69a]">{request}</span></>
        ) : (
            <>Results for best: <span className="text-[#26a69a]">{request}</span> near <span className="text-[#ff5b44]">{location}</span></>
        )}
        </h1>
                    
            {!results || results.length === 0 ? (
                <p>No recommendations found.</p>
            ) : (
                <div className="grid gap-8 mt-4 max-w-4xl mx-auto">
                    {results.map((result, index) => (
                        <div 
                            key={index}
                            className="bg-[#0a1f2b] p-6 rounded-lg shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-[1.01]"
                        >
                            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
                                <h2 className="text-2xl font-bold text-[#26a69a] mb-2 md:mb-0">{result.name}</h2>
                                <div className="flex items-center">
                                    {result.rating && (
                                        <div className="flex items-center bg-[#26a69a] text-[#0a1f2b] px-3 py-1 rounded-full mr-3">
                                            <FaStar className="mr-1" />
                                            <span className="font-bold">{result.rating}</span>
                                        </div>
                                    )}
                                    {result.link && (
                                        <a 
                                            href={result.link} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                            className="bg-[#1e88e5] text-[#f8f0dd] px-3 py-1 rounded-full flex items-center hover:bg-[#1976d2] transition-all duration-300"
                                        >
                                            <span className="mr-1">Visit</span>
                                            <FaExternalLinkAlt size={12} />
                                        </a>
                                    )}
                                </div>
                            </div>
                            
                            <div className="mb-4">
                                <div className="flex items-center mb-2">
                                    <FaList className="text-[#ff5b44] mr-2" />
                                    <h3 className="text-lg font-semibold">Key Features</h3>
                                </div>
                                <ul className="grid grid-cols-1 md:grid-cols-3 gap-2">
                                    {result.key_features.map((feature, idx) => (
                                        <li key={idx} className="bg-[#162c38] px-3 py-2 rounded-md text-left">{feature}</li>
                                    ))}
                                </ul>
                            </div>
                            
                            <div>
                                <div className="flex items-center mb-2">
                                    <FaQuoteRight className="text-[#ff5b44] mr-2" />
                                    <h3 className="text-lg font-semibold">What People Say</h3>
                                </div>
                                <div className="grid gap-3">
                                    {result.quotes.map((quote, idx) => (
                                        <blockquote key={idx} className="bg-[#162c38] p-4 rounded-md text-left italic border-l-4 border-[#26a69a]">
                                            "{quote}"
                                        </blockquote>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div className="mt-10 mb-6">
                <a 
                    href="/" 
                    className="bg-[#1e88e5] text-[#f8f0dd] font-medium rounded-lg text-lg px-6 py-3 hover:bg-[#1976d2] transition-all duration-300 inline-block"
                >
                    Back to Homepage
                </a>
            </div>
        </div>
    )
}

export default SecondPage
