"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const LoadingAnimation = () => {
    const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
    
    const loadingMessages = [
        'Scraping Reddit for my Favourite Judges in the World...',
        'Walking through the Sahara Desert...',
        'Exploring new recommendations...',
        'Diving into the sea of reviews...',
        'Hiking Mount Everest for the best products...',
        'Tuning into the best opinions...',
        'Sifting through real user feedback...',
        'Lets Goo BearHacks!!!',
        'Um this shouldnt take this long...',
        'I mean we are scrapping thru a ton of data...',
        'Should be here any moment, I promise T_T',
    ];
    
    useEffect(() => {
        const interval = setInterval(() => {
          setCurrentMessageIndex((prevIndex) => 
            (prevIndex + 1) % loadingMessages.length
          );
        }, 3500);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen w-full absolute top-0 left-0">
          <div className="relative w-32 h-32 mb-8">
            <motion.div
              className="absolute w-full h-full rounded-full border-t-4 border-r-4"
              style={{ borderColor: '#FF5B44' }}
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            />
            <motion.div
              className="absolute w-full h-full rounded-full border-b-4 border-l-4"
              style={{ borderColor: '#26A69A' }}
              animate={{ rotate: -360 }}
              transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
            />
            {/* If you have a logo */}
            <motion.div
              className="absolute w-16 h-16 top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <img src="/WBuyLogo.png" alt="WBud" className="w-full h-full object-contain" />
            </motion.div>
          </div>
          
          <AnimatePresence mode="wait">
            <motion.div
              key={currentMessageIndex}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="text-xl font-medium text-center"
              style={{ color: '#26A69A' }}
            >
              {loadingMessages[currentMessageIndex]}
            </motion.div>
          </AnimatePresence>

          <motion.div 
            className="mt-8 flex space-x-2"
          >
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: '#FF5B44' }}
                animate={{ y: ["0%", "-50%", "0%"] }}
                transition={{ duration: 1, delay: i * 0.2, repeat: Infinity }}
              />
            ))}
          </motion.div>
        </div>
    );
};

export default LoadingAnimation;

