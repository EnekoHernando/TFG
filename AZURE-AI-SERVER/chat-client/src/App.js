import React, { useState } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Paper, List, ListItem, ListItemText, AppBar, Toolbar } from '@mui/material';
import './App.css';

const App = () => {
    const [username, setUsername] = useState('');
    const [index, setIndex] = useState('');
    const [message, setMessage] = useState('');
    const [chat, setChat] = useState([]);
    const [connected, setConnected] = useState(false);
    const [sessionId, setSessionId] = useState(null);

    const connect = async () => {
        try {
            const response = await axios.post('http://localhost:5000/connect', { username, index });
            setSessionId(response.data.session_id);
            setConnected(true);
            alert('Connected');
        } catch (error) {
            console.error(error);
            alert('Failed to connect');
        }
    };

    const sendMessage = async () => {
        try {
            const response = await axios.post('http://localhost:5000/send_message', { session_id: sessionId, message });
            setChat([...chat, { sender: 'User', text: message }, { sender: 'Bot', text: response.data.response }]);
            setMessage('');
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6">
                        Chat Client
                    </Typography>
                </Toolbar>
            </AppBar>
            <Container maxWidth="sm">
                <Paper style={{ padding: 16, marginTop: 16 }}>
                    {!connected ? (
                        <div>
                            <TextField
                                fullWidth
                                label="Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                margin="normal"
                            />
                            <TextField
                                fullWidth
                                label="Index"
                                value={index}
                                onChange={(e) => setIndex(e.target.value)}
                                margin="normal"
                            />
                            <Button variant="contained" color="primary" onClick={connect} fullWidth>
                                Connect
                            </Button>
                        </div>
                    ) : (
                        <div>
                            <Paper style={{ maxHeight: 400, overflow: 'auto', marginBottom: 16 }}>
                                <List>
                                    {chat.map((msg, index) => (
                                        <ListItem key={index} style={{ textAlign: msg.sender === 'User' ? 'right' : 'left' }}>
                                            <ListItemText
                                                primary={
                                                    <Typography
                                                        component="div"
                                                        style={{ whiteSpace: 'pre-wrap' }}
                                                        dangerouslySetInnerHTML={{ __html: `<b>${msg.sender}:</b> ${msg.text}` }}
                                                    />
                                                }
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            </Paper>
                            <TextField
                                fullWidth
                                label="Message"
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                margin="normal"
                            />
                            <Button variant="contained" color="primary" onClick={sendMessage} fullWidth>
                                Send
                            </Button>
                        </div>
                    )}
                </Paper>
            </Container>
        </div>
    );
};

export default App;
