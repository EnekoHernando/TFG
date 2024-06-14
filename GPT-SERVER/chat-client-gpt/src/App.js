import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Paper, List, ListItem, ListItemText, AppBar, Toolbar, MenuItem, Select, FormControl, InputLabel } from '@mui/material';
import TextareaAutosize from '@mui/material/TextareaAutosize';
import './App.css';

const App = () => {
    const [username, setUsername] = useState('');
    const [index, setIndex] = useState('');
    const [indices, setIndices] = useState([]);
    const [message, setMessage] = useState('');
    const [chat, setChat] = useState([]);
    const [connected, setConnected] = useState(false);
    const [sessionId, setSessionId] = useState(null);

    useEffect(() => {
        const fetchIndices = async () => {
            try {
                const response = await axios.get('http://localhost:5000/get_indices');
                setIndices(response.data.indices);
            } catch (error) {
                console.error('Error fetching indices:', error);
            }
        };

        fetchIndices();
    }, []);

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
                            <FormControl fullWidth margin="normal">
                                <InputLabel>Index</InputLabel>
                                <Select
                                    value={index}
                                    onChange={(e) => setIndex(e.target.value)}
                                >
                                    {indices.map((idx, i) => (
                                        <MenuItem key={i} value={idx}>{idx}</MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                            <Button variant="contained" color="primary" onClick={connect} fullWidth>
                                Connect
                            </Button>
                        </div>
                    ) : (
                        <div>
                            <Paper className="chat">
                                <List>
                                    {chat.map((msg, index) => (
                                        <ListItem key={index} className={msg.sender === 'User' ? 'user-message' : 'bot-message'}>
                                            <ListItemText
                                                primary={
                                                    <Typography
                                                        component="div"
                                                        className="message-content"
                                                        style={{ whiteSpace: 'pre-wrap' }}
                                                        dangerouslySetInnerHTML={{ __html: `<b>${msg.sender}:</b> ${msg.text}` }}
                                                    />
                                                }
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            </Paper>
                            <TextareaAutosize
                                minRows={3}
                                placeholder="Message"
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                style={{ width: '100%', marginTop: 10, padding: 10 }}
                            />
                            <Button variant="contained" color="primary" onClick={sendMessage} fullWidth style={{ marginTop: 10 }}>
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
