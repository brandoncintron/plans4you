import React from "react";
import { Input } from "@/components/ui/input";
import {
  FormControl,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { ControllerRenderProps } from "react-hook-form";
import { HealthcareFormValues } from "@/schema/healthcare-form";

interface NumberInputProps {
  field: ControllerRenderProps<HealthcareFormValues, keyof HealthcareFormValues>;
  label: string;
  placeholder: string;
}

const NumberInput: React.FC<NumberInputProps> = ({
  field,
  label,
  placeholder,
}) => {
  return (
    <FormItem>
      <FormLabel>{label}</FormLabel>
      <FormControl>
        <Input
          type="number"
          placeholder={placeholder}
          {...field}
          value={typeof field.value === 'number' ? field.value : ""}
          onChange={(e) => {
            const value = e.target.value;
            // Only allow digits
            if (value === "" || /^\d+$/.test(value)) {
              field.onChange(value === "" ? 0 : parseInt(value, 10));
            }
          }}
          onKeyDown={(e) => {
            // Prevent 'e', '+', '-' from being entered
            if (["e", "E", "+", "-"].includes(e.key)) {
              e.preventDefault();
            }
          }}
        />
      </FormControl>
      <FormMessage />
    </FormItem>
  );
};

export default NumberInput; 