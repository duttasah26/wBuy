"use client";

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Location from './components/Location';
import { motion, AnimatePresence } from "framer-motion";
import { FaGithub } from 'react-icons/fa';

export default function Home() {
  const [locationData, setLocationData] = useState(null);
  const [manualLocation, setManualLocation] = useState("");
  const [showManualInput, setShowManualInput] = useState(false);
  const [userText, setUserText] = useState("");
  const [category, setCategory] = useState("");
  const router = useRouter();
  const [wobble, setWobble] = useState(false);
  const [currentWord, setCurrentWord] = useState("Food");
  const words = ["Purchase", "Travel", "Food"];


  useEffect(() => {
    const wobbleInterval = setInterval(() => {
      setWobble(true);
      setTimeout(() => setWobble(false), 1000);
    }, 10000);
    
    return () => clearInterval(wobbleInterval);
  }, []);

  useEffect(() => {
    let index = 0;
    const wordInterval = setInterval(() => {
      index = (index + 1) % words.length;
      setCurrentWord(words[index]);
    }, 3000);
    
    return () => clearInterval(wordInterval);
  }, []);

  const handleInputChange = (e) => {
    setUserText(e.target.value);
  }

  const handleManualLocationChange = (e) => {
    setManualLocation(e.target.value);
  }

  const setManualLocationData = () => {
    if (manualLocation.trim()) {
      setLocationData(manualLocation);
      setShowManualInput(false);
    }
  }

  const getRecommendations = () => {
    if (!category) {
      alert("Please select a category (Food, Product, or Location).");
      return;
    }
    
    if (!userText) {
      alert("Please enter a request.");
      return;
    }
  
    if (category === "product") {
      router.push(`/results?request=${encodeURIComponent(userText)}&category=${encodeURIComponent(category)}`);
    } else {
      if (locationData || manualLocation.trim()) {
        const finalLocation = locationData || manualLocation.trim();
        router.push(`/results?request=${encodeURIComponent(userText)}&category=${encodeURIComponent(category)}&location=${encodeURIComponent(finalLocation)}`);
      } else {
        alert("Please provide your location for Food or Location requests.");
      }
    }
  }
  
  return (
    
    <div className="min-h-screen flex items-center justify-center bg-[#0e2c3b] text-[#f8f0dd]">
    <a 
    href="https://github.com/evanbabic/wBuy" 
    target="_blank" 
    rel="noopener noreferrer" 
    className="absolute top-4 right-4 text-[#f8f0dd] hover:text-[#ff5b44] transition-colors duration-300"
   >
    <FaGithub size={28} />
    </a>
  
      
      <main className="w-full max-w-4xl px-4 flex flex-col items-center">
        <div className="container text-center">
          
          <section className="py-8">
            <div className="mb-6 relative">
              <img 
                src="/WBuyLogo.png" 
                alt="WBuy Logo" 
                width={120} 
                height={120} 
                className={`mx-auto transition-all duration-300 ${wobble ? 'animate-wobble' : ''}`}
                style={{
                  animation: wobble ? 'wobble 1s ease' : 'none'
                }}
              />
              <div className="mt-3 text-[#f8f0dd] font-semibold">AI Powered</div>
            </div>
            
            <h1 className="text-5xl font-bold mb-16 text-[#f8f0dd]">
              Your Ultimate<br />
              <AnimatePresence mode="wait">
                <motion.span
                  key={currentWord}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 0 }}
                  transition={{ duration: 0.5 }}
                  className="inline-block min-w-[200px]"
                >
                  {currentWord}
                </motion.span>
              </AnimatePresence> Companion
            </h1>
            
            <div className="mb-8 relative">
              <div className="text-lg mb-2">What do you want the best of?</div>
              <input
                type="text"
                value={userText}
                onChange={handleInputChange}
                className="w-full max-w-md py-2 px-3 bg-transparent border-b-2 border-[#26a69a] text-[#f8f0dd] text-center focus:outline-none"
                placeholder="Enter your request (eg. Burger, Iphone, Parks)"
              />
            </div>

            <div className="mb-8">
              {!locationData ? (
                <div>
                  <div className="flex justify-center gap-4 mb-4">
                    <Location setLocationData={setLocationData}/> 
                    <button 
                      onClick={() => setShowManualInput(!showManualInput)}
                      className="text-white mt-5 bg-[#26a69a] hover:bg-[#1e8a7e] focus:ring-4 focus:ring-teal-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-[#26a69a] dark:hover:bg-[#1e8a7e] focus:outline-none dark:focus:ring-teal-800"
                    >
                      Enter Location Manually
                    </button>
                  </div>
                  
                  {showManualInput && (
                    <div className="mt-4 flex justify-center gap-2">
                      <input
                        type="text"
                        value={manualLocation}
                        onChange={handleManualLocationChange}
                        className="py-2 px-3 bg-transparent border-b-2 border-[#26a69a] text-[#f8f0dd] text-center focus:outline-none"
                        placeholder="City, State"
                      />
                      <button 
                        onClick={setManualLocationData}
                        className="text-[#f8f0dd] bg-[#ff5b44] hover:bg-[#e64a33] font-medium rounded-lg text-sm px-4 py-2 transition-all duration-300 flex items-center gap-1"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Set
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <p className="py-2">Location: {locationData}</p>
              )}
            </div>

            <div className="flex justify-center gap-4 mb-10">
              <label className="cursor-pointer">
                <input
                  type="radio"
                  name="category"
                  value="food"
                  checked={category === "food"}
                  onChange={(e) => setCategory(e.target.value)}
                  className="hidden"
                />
                <span className={`px-5 py-2 rounded-full flex items-center gap-2 transition-all duration-300 ${
                  category === "food" 
                    ? 'bg-[#ff5b44] text-[#f8f0dd]' 
                    : 'bg-transparent text-[#f8f0dd] border border-[#ff5b44] hover:bg-[#ff5b44]/20'
                }`}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  Food
                </span>
              </label>
              
              <label className="cursor-pointer">
                <input
                  type="radio"
                  name="category"
                  value="product"
                  checked={category === "product"}
                  onChange={(e) => setCategory(e.target.value)}
                  className="hidden"
                />
                <span className={`px-5 py-2 rounded-full flex items-center gap-2 transition-all duration-300 ${
                  category === "product" 
                    ? 'bg-[#ff5b44] text-[#f8f0dd]' 
                    : 'bg-transparent text-[#f8f0dd] border border-[#ff5b44] hover:bg-[#ff5b44]/20'
                }`}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                  Product
                </span>
              </label>
              
              <label className="cursor-pointer">
                <input
                  type="radio"
                  name="category"
                  value="location"
                  checked={category === "location"}
                  onChange={(e) => setCategory(e.target.value)}
                  className="hidden"
                />
                <span className={`px-5 py-2 rounded-full flex items-center gap-2 transition-all duration-300 ${
                  category === "location" 
                    ? 'bg-[#ff5b44] text-[#f8f0dd]' 
                    : 'bg-transparent text-[#f8f0dd] border border-[#ff5b44] hover:bg-[#ff5b44]/20'
                }`}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Location
                </span>
              </label>
            </div>

            <button 
              type="button" 
              className="mx-auto block bg-[#ff5b44] text-[#f8f0dd] font-medium rounded-lg text-lg px-8 py-4 hover:bg-[#e64a33] transition-all duration-300 transform hover:scale-105 hover:shadow-lg active:scale-95 focus:outline-none focus:ring-2 focus:ring-[#ff5b44] focus:ring-opacity-50"
              onClick={getRecommendations}
            >
              Get Recommendations
            </button>
          </section>
        </div>
      </main>
    </div>
  );
}
