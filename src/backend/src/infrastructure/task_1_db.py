src/models/user.ts:
```typescript
import { Model } from 'sequelize';

interface UserAttributes {
  username: string;
  email: string;
  password: string;
  role: string;
  title: string;
  status: string;
  assignedUserID: number;
}

export class User extends Model<UserAttributes> implements UserAttributes {
  public id!: number;
  public username!: string;
  public email!: string;
  public password!: string;
  public role!: string;
  public title!: string;
  public status!: string;
  public assignedUserID!: number;
}
```
src/app.ts:
```typescript
import express from 'express';
import { User } from './models/user';

const app = express();

// Define API endpoints for user registration and authentication
app.post('/register', async (req, res) => {
  const { username, email, password, role, title, status, assignedUserID } = req.body;

  // Validate input data
  if (!username || !email || !password || !role || !title || !status || !assignedUserID) {
    return res.status(400).json({ message: 'Invalid request body' });
  }

  try {
    const user = await User.create({ username, email, password, role, title, status, assignedUserID });
    res.json(user);
  } catch (error) {
    console.log(error);
    res.status(500).json({ message: 'Error creating user' });
  }
});

app.post('/login', async (req, res) => {
  const { email, password } = req.body;

  // Validate input data
  if (!email || !password) {
    return res.status(400).json({ message: 'Invalid request body' });
  }

  try {
    const user = await User.findOne({ where: { email, password } });
    if (user) {
      res.json(user);
    } else {
      res.status(401).json({ message: 'Invalid credentials' });
    }
  } catch (error) {
    console.log(error);
    res.status(500).json({ message: 'Error logging in user' });
  }
});
```