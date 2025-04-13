import React from 'react'
import { Slider } from "@/components/ui/slider"

interface RiskToleranceSliderProps {
  value?: number[];
  onValueChange?: (values: number[]) => void;
}

const RiskToleranceSlider: React.FC<RiskToleranceSliderProps> = ({ 
  value = [50], 
  onValueChange 
}) => {
  return (
    <div className='flex flex-col w-full'>
      <Slider 
        defaultValue={value} 
        value={value}
        onValueChange={onValueChange}
        max={100} 
        step={1} 
        className="w-full" 
      />
      <div className="flex justify-between w-full mt-2 text-xs text-gray-500">
        <span>Low Risk</span>
        <span>Moderate Risk</span>
        <span>High Risk</span>
      </div>
    </div>
  )
}

export default RiskToleranceSlider
