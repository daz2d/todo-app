```typescript
import { Request, Response } from 'express';
import { validateUserInput } from './utils';
import { User } from './models';

const users = new Map<string, User>();

app.post('/api/users', async (req: Request, res: Response) => {
  const userData = req.body;
  const validationResult = validateUserInput(userData);
  if (!validationResult.isValid) {
    return res.status(400).json({ message: 'Invalid user input' });
  }

  const userId = generateUniqueId();
  const newUser = new User(userId, userData.name, userData.email);
  users.set(userId, newUser);

  return res.status(201).json({ message: 'User created successfully' });
});
```