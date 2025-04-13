import React from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
  healthcareFormSchema,
  HealthcareFormValues,
} from "@/schema/healthcare-form";
import { usStates } from "@/data/usStates";
import NumberInput from "@/components/NumberInput";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import RiskToleranceSlider from "./RiskToleranceSlider";

interface HealthcareFormProps {
  onFormSubmit: (data: HealthcareFormValues) => void;
  isLoading: boolean;
}

const HealthcareForm: React.FC<HealthcareFormProps> = ({
  onFormSubmit,
  isLoading,
}) => {
  const form = useForm<HealthcareFormValues>({
    resolver: zodResolver(healthcareFormSchema) as any,
    defaultValues: {
      name: "",
      age: 0,
      dependents: 0,
      zipCode: "",
      state: "",
      income: "",
      dentalPlanRequired: "no",
      riskTolerance: 50,
      consentGiven: false,
    },
  });

  const handleSubmit = (data: HealthcareFormValues) => {
    onFormSubmit(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Full Name</FormLabel>
              <FormControl>
                <Input placeholder="Jane Doe" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="age"
          render={({ field }) => (
            <NumberInput field={field} label="Age" placeholder="35" />
          )}
        />

        <FormField
          control={form.control}
          name="dependents"
          render={({ field }) => (
            <NumberInput field={field} label="Dependents" placeholder="2" />
          )}
        />

        <FormField
          control={form.control}
          name="zipCode"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Zip Code</FormLabel>
              <FormControl>
                <Input placeholder="99501" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="state"
          render={({ field }) => (
            <FormItem>
              <FormLabel>State</FormLabel>
              <Select onValueChange={field.onChange} value={field.value || ""}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select state" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {usStates.map((state) => (
                    <SelectItem key={state.value} value={state.value}>
                      {state.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="income"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Annual Income</FormLabel>
              <FormControl>
                <Input 
                  placeholder="$28,000" 
                  {...field} 
                  onChange={(e) => {
                    // Get the raw value without formatting
                    const rawValue = e.target.value.replace(/[^0-9.]/g, '');
                    
                    if (rawValue === '') {
                      // If empty, set empty string
                      field.onChange('');
                    } else {
                      // Format as currency
                      const formatter = new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                      });
                      
                      const formatted = formatter.format(Number(rawValue));
                      field.onChange(formatted);
                    }
                  }}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="dentalPlanRequired"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Dental Plan Required</FormLabel>
              <Select
                onValueChange={field.onChange}
                value={field.value || "no"}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select option" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="yes">Yes</SelectItem>
                  <SelectItem value="no">No</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="riskTolerance"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Risk Tolerance</FormLabel>
              <FormControl>
                <div className="w-full">
                  <RiskToleranceSlider 
                    value={[field.value]} 
                    onValueChange={(values) => {
                      field.onChange(values[0]);
                    }}
                  />
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="py-2 px-3 bg-blue-50 border border-blue-100 rounded-md">
          <h3 className="text-sm font-semibold text-blue-800 mb-2">
            HIPAA Privacy Notice
          </h3>
          <p className="text-xs text-gray-700 mb-2">
            The information you provide is protected under the Health Insurance
            Portability and Accountability Act (HIPAA). We will use this
            information solely for the purpose of providing healthcare plan
            recommendations. Your information is encrypted and securely
            processed. We do not share your personal health information with
            third parties without your consent, except as required by law.
          </p>
        <FormField
          control={form.control}
          name="consentGiven"
          render={({ field }) => (
            <FormItem className="flex flex-row items-start space-x-3 space-y-0 py-2">
              <FormControl>
                <Checkbox
                  checked={field.value}
                  onCheckedChange={field.onChange}
                  className="bg-white"
                />
              </FormControl>
              <div className="space-y-1 leading-none">
                <FormLabel className="text-sm font-medium">
                  I consent to the collection and processing of my health
                  information as described in the privacy notice.
                </FormLabel>
                <FormMessage />
              </div>
            </FormItem>
          )}
        />
        </div>


        <div className="flex justify-center pt-4">
          <Button
            type="submit"
            disabled={isLoading || !form.watch("consentGiven")}
          >
            {isLoading ? "Processing..." : "Get AI Recommendations"}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default HealthcareForm;
