declare module "react-simple-maps" {
  import { ReactNode, CSSProperties } from "react";

  export interface GeographyProps {
    geography: any;
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
    style?: {
      default?: CSSProperties;
      hover?: CSSProperties;
      pressed?: CSSProperties;
    };
    onClick?: () => void;
    key?: string;
  }

  export interface ComposableMapProps {
    projection?: string;
    projectionConfig?: Record<string, number | number[]>;
    width?: number;
    height?: number;
    className?: string;
    children?: ReactNode;
  }

  export interface ZoomableGroupProps {
    center?: [number, number];
    zoom?: number;
    children?: ReactNode;
  }

  export interface GeographiesProps {
    geography: object | string;
    children: (args: { geographies: any[] }) => ReactNode;
  }

  export const ComposableMap: React.FC<ComposableMapProps>;
  export const ZoomableGroup: React.FC<ZoomableGroupProps>;
  export const Geographies: React.FC<GeographiesProps>;
  export const Geography: React.FC<GeographyProps>;
}
