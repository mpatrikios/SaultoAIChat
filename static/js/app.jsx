const App = () => {
    return (
        <div className="app-container">
            <Header />
            <ChatInterface />
        </div>
    );
};

// Update to React 18 usage
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
