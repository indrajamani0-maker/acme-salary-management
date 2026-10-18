import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('ACME salary dashboard', () => {
  it('renders the salary overview heading', () => {
    render(<App />);
    expect(screen.getByRole('heading', { name: /salary overview/i })).toBeTruthy();
  });
});
