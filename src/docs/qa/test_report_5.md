 To test the login functionality, we can create a Jest test suite for the `LoginForm` component. We'll use the `react-testing-library` to render the component and simulate user interactions. Here's an example of how you could write the tests:

```javascript
import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import LoginForm from './LoginForm';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

const mockStore = configureStore([thunk]);

describe('LoginForm', () => {
  let store;

  beforeEach(() => {
    store = mockStore({ user: {} });
  });

  it('should render the login form', () => {
    const { getByLabelText, getByText } = render(
      <Provider store={store}>
        <LoginForm />
      </Provider>
    );

    expect(getByLabelText(/username/i)).toBeInTheDocument();
    expect(getByLabelText(/password/i)).toBeInTheDocument();
    expect(getByText(/login/i)).toBeInTheDocument();
  });

  it('should call loginUser action when form is submitted with valid credentials', () => {
    const user = { id: 1, username: 'testuser', token: 'testtoken' };
    store.dispatch = jest.fn(() => Promise.resolve());

    const { getByLabelText, getByText } = render(
      <Provider store={store}>
        <LoginForm />
      </Provider>
    );

    fireEvent.change(getByLabelText(/username/i), { target: { value: 'testuser' } });
    fireEvent.change(getByLabelText(/password/i), { target: { value: 'testpassword' } });
    fireEvent.click(getByText(/login/i));

    expect(store.dispatch).toHaveBeenCalledWith({ type: 'LOGIN_USER_SUCCESS', payload: user });
  });

  it('should not call loginUser action when form is submitted with invalid credentials', () => {
    store.dispatch = jest.fn(() => Promise.resolve());

    const { getByLabelText, getByText } = render(
      <Provider store={store}>
        <LoginForm />
      </Provider>
    );

    fireEvent.change(getByLabelText(/username/i), { target: { value: 'invaliduser' } });
    fireEvent.change(getByLabelText(/password/i), { target: { value: 'invalidpassword' } });
    fireEvent.click(getByText(/login/i));

    expect(store.dispatch).not.toHaveBeenCalledWith({ type: 'LOGIN_USER_SUCCESS', payload: expect.anything() });
  });
});
```

In this test suite, we first render the `LoginForm` component and check if all the necessary components are rendered correctly. Then, we simulate user interactions by changing the input values and clicking the login button. We also mock the Redux store to check if the `LOGIN_USER_SUCCESS` action is dispatched when the form is submitted with valid credentials. If the form is submitted with invalid credentials, we ensure that the action is not dispatched.