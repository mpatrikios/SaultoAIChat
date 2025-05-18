const App = () => {
    return (
        <div className="app-container">
            <Header />
            <ChatInterface />
        </div>
    );
};

ReactDOM.render(<App />, document.getElementById('root'));
