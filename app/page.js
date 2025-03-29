export default function Home() {
  return (
    <div>
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 flex items-center justify-center">
        <main className="container">
          <section className="py-4">
            <div className="container overflow-hidden">
              <div className="mb-10 flex flex-col items-center gap-6 text-center">
                <div className="inline-flex font-semibold">AI Powered</div>
              </div>
              <div className="text-center">
                <h1 className="text-4xl font-semibold lg:text-6xl">
                  Your Ultimate <br/> Purchase Companion
                </h1>
              </div>
            </div>
          </section>

          <section className="py-4 text-center">
            <div className="text-center pt-10 font-semibold">What are you looking for?</div>
            <div className="flex items-center justify-center">
              <input type="text" id="large-input" class="p-4 w-sm center text-white text-center font-semibold border-b-2 focus:outline-none"/>
            </div>

          
            <div className="text-center pt-10 font-semibold">Where are you located?</div>
            <div className="flex items-center justify-center">
                <input type="text" id="large-input" class="p-4 w-sm center text-white text-center font-semibold border-b-2 focus:outline-none"/>
            </div>

            <button type="button" class="text-white mt-5 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Get Recommendations</button>

          </section>

        </main>
      </main>
      
    </div>
  );
}
