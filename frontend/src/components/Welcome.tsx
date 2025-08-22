import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { motion } from 'framer-motion'
import React from 'react'

interface WelcomeProps {
  onCreateClick: () => void
  message?: string
}

export default function Welcome({ onCreateClick, message }: WelcomeProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <Card>
        <CardHeader>
          <CardTitle className="text-center">Добро пожаловать в Telepets!</CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          <div className="text-6xl mb-4">🥚</div>
          <p className="text-slate-400">{message || 'Создайте своего первого питомца и начните увлекательное путешествие!'}</p>
          <Button onClick={onCreateClick} size="lg">Создать питомца</Button>
        </CardContent>
      </Card>
    </motion.div>
  )
}


